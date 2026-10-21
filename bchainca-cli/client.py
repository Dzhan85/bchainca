import base64
import datetime
import hashlib
import json
import secrets
import time
from base64 import b64encode

import requests

from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_signing import ParseError
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey

from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchList
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.batch_pb2 import Batch

from CaException import CaException

FAMILY_NAME = 'CA'
FAMILY_VERSION = '1.0'
NAMESPACE = 'ca_1'

# Must match CA_KEY_PASSPHRASE in docker/bchainca-tp/bchainca/CaState.py.
CA_KEY_PASSPHRASE = b'passw'

CA_ROOT_ENTITY = 'CA_Root'
CA_ADMIN_ENTITY = 'CA_Admin'

# Seconds added on top of the commit wait for the HTTP request itself.
HTTP_TIMEOUT_MARGIN = 10


def _sha512(data):
    return hashlib.sha512(data).hexdigest()


def get_prefix():
    return _sha512(NAMESPACE.encode('utf-8'))[:6]


def get_address(entity):
    """State address of a CA entity (certificate serial, 'CA_Root', ...)."""
    return get_prefix() + _sha512(str(entity).encode('utf-8'))[:64]


def make_payload(action, value, date=None):
    """Serialization is a '|' delimited utf-8 string: action|date|value."""
    if date is None:
        # Naive UTC, as expected by the transaction processor.
        date = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    return "|".join([action, date.isoformat(), str(value)]).encode('utf-8')


def new_serial():
    """Random, positive 63-bit number used as transaction nonce.

    The transaction processor uses the nonce as the certificate serial
    number, so knowing it up front lets us find the certificate in state.
    """
    return secrets.randbelow(2 ** 63 - 1) + 1


class CaClient:
    def __init__(self, base_url, keyfile=None):

        self._base_url = base_url if '://' in base_url else 'http://' + base_url
        self._base_url = self._base_url.rstrip('/')

        if keyfile is None:
            self._signer = None
            return

        try:
            with open(keyfile) as fd:
                private_key_str = fd.read().strip()
        except OSError as err:
            raise CaException(
                'Failed to read private key {}: {}'.format(
                    keyfile, str(err)))

        try:
            private_key = Secp256k1PrivateKey.from_hex(private_key_str)
        except ParseError as e:
            raise CaException(
                'Unable to load private key: {}'.format(str(e)))

        self._signer = CryptoFactory(create_context('secp256k1')) \
            .new_signer(private_key)

    @property
    def public_key(self):
        return self._signer.get_public_key().as_hex() if self._signer else None

    # Transactions

    def init(self, pkey, wait=None, auth_user=None, auth_password=None):
        """Initialize the CA with a CA_KEY_PASSPHRASE encrypted PEM key."""
        return self._send_ca_txn(
            "init",
            value=pkey,
            wait=wait,
            auth_user=auth_user,
            auth_password=auth_password)

    def create(self, csr, wait=None, auth_user=None, auth_password=None):
        """Request a certificate for a PEM encoded CSR.

        Returns:
            (serial, status): serial of the new certificate and the batch status.
        """
        return self._send_ca_txn(
            "create",
            value=csr,
            wait=wait,
            auth_user=auth_user,
            auth_password=auth_password)

    def revoke(self, serial, wait=None, auth_user=None, auth_password=None):
        return self._send_ca_txn(
            "revoke",
            value=serial,
            wait=wait,
            auth_user=auth_user,
            auth_password=auth_password)

    def simple(self, data, wait=None, auth_user=None, auth_password=None):
        address = get_simple_address('Simple Data Value 1')
        transaction = self._create_transaction(
            'SIMPLE', str(data).encode(), address, nonce=new_serial())
        return self._submit([transaction], wait, auth_user, auth_password)

    # Read-only queries against global state (no transaction needed)

    def get_record(self, serial, auth_user=None, auth_password=None):
        """Certificate record stored by the transaction processor, or None."""
        data = self._get_state(get_address(serial), auth_user, auth_password)
        return json.loads(data.decode('utf-8')) if data is not None else None

    def list_records(self, auth_user=None, auth_password=None):
        """All certificate records in the CA namespace, sorted by serial."""
        records = []
        for entry in self._list_state(get_prefix(), auth_user, auth_password):
            try:
                record = json.loads(base64.b64decode(entry['data']).decode('utf-8'))
            except ValueError:
                continue  # CA root certificate / key entries are PEM, not JSON
            if isinstance(record, dict) and 'serial_number' in record:
                records.append(record)
        return sorted(records, key=lambda r: int(r['serial_number']))

    def get_ca_certificate(self, auth_user=None, auth_password=None):
        """PEM encoded CA root certificate, or None if the CA is not initialized."""
        return self._get_state(get_address(CA_ROOT_ENTITY), auth_user, auth_password)

    def get_ca_admin(self, auth_user=None, auth_password=None):
        data = self._get_state(get_address(CA_ADMIN_ENTITY), auth_user, auth_password)
        return data.decode('utf-8') if data is not None else None

    # Internals

    def _get_state(self, address, auth_user=None, auth_password=None):
        result = self._send_request(
            'state/{}'.format(address),
            auth_user=auth_user,
            auth_password=auth_password,
            not_found_ok=True)
        if result is None:
            return None
        return base64.b64decode(result.json()['data'])

    def _list_state(self, prefix, auth_user=None, auth_password=None):
        url = 'state?address={}'.format(prefix)
        while url:
            result = self._send_request(url, auth_user=auth_user, auth_password=auth_password,
                                        not_found_ok=True)
            if result is None:
                return
            body = result.json()
            yield from body.get('data', [])
            url = body.get('paging', {}).get('next')

    def _get_status(self, batch_id, wait, auth_user=None, auth_password=None):
        result = self._send_request(
            'batch_statuses?id={}&wait={}'.format(batch_id, wait),
            auth_user=auth_user,
            auth_password=auth_password,
            timeout=wait + HTTP_TIMEOUT_MARGIN)
        try:
            return result.json()['data'][0]
        except (ValueError, KeyError, IndexError) as err:
            raise CaException('Unexpected batch status response: {}'.format(err))

    def _send_request(self,
                      suffix,
                      data=None,
                      content_type=None,
                      auth_user=None,
                      auth_password=None,
                      not_found_ok=False,
                      timeout=HTTP_TIMEOUT_MARGIN * 3):
        if '://' in suffix:  # absolute URL, e.g. from REST API paging links
            url = suffix
        else:
            url = "{}/{}".format(self._base_url, suffix)

        headers = {}
        if auth_user is not None:
            auth_string = "{}:{}".format(auth_user, auth_password)
            b64_string = b64encode(auth_string.encode()).decode()
            auth_header = 'Basic {}'.format(b64_string)
            headers['Authorization'] = auth_header

        if content_type is not None:
            headers['Content-Type'] = content_type

        try:
            if data is not None:
                result = requests.post(url, headers=headers, data=data, timeout=timeout)
            else:
                result = requests.get(url, headers=headers, timeout=timeout)
        except requests.ConnectionError as err:
            raise CaException(
                'Failed to connect to {}: {}'.format(url, str(err)))
        except requests.RequestException as err:
            raise CaException('Request to {} failed: {}'.format(url, str(err)))

        if result.status_code == 404:
            if not_found_ok:
                return None
            raise CaException("Not found: {}".format(url))
        if not result.ok:
            raise CaException("Error {}: {}".format(
                result.status_code, _error_message(result)))

        return result

    def _send_ca_txn(self,
                     action,
                     value="",
                     wait=None,
                     auth_user=None,
                     auth_password=None):
        serial = new_serial()
        transaction = self._create_transaction(
            FAMILY_NAME, make_payload(action, value), get_prefix(), nonce=serial)
        status = self._submit([transaction], wait, auth_user, auth_password)
        return serial, status

    def _create_transaction(self, family_name, payload, address, nonce):
        if self._signer is None:
            raise CaException('A private key is required to send transactions')

        header = TransactionHeader(
            signer_public_key=self.public_key,
            family_name=family_name,
            family_version=FAMILY_VERSION,
            inputs=[address],
            outputs=[address],
            dependencies=[],
            payload_sha512=_sha512(payload),
            batcher_public_key=self.public_key,
            nonce=hex(nonce)
        ).SerializeToString()

        return Transaction(
            header=header,
            payload=payload,
            header_signature=self._signer.sign(header)
        )

    def _submit(self, transactions, wait, auth_user, auth_password):
        """Submit a batch and, if wait > 0, wait up to wait seconds for it to commit.

        Returns:
            str: batch status ('COMMITTED', 'PENDING', ...), or 'SUBMITTED'
            when not waiting.
        Raises:
            CaException: if the batch is rejected as invalid.
        """
        batch_list = self._create_batch_list(transactions)
        batch_id = batch_list.batches[0].header_signature

        self._send_request(
            "batches", batch_list.SerializeToString(),
            'application/octet-stream',
            auth_user=auth_user,
            auth_password=auth_password)

        if not wait or wait <= 0:
            return 'SUBMITTED'

        deadline = time.time() + wait
        while True:
            remaining = max(1, int(deadline - time.time()))
            batch_status = self._get_status(batch_id, remaining, auth_user, auth_password)
            status = batch_status['status']
            if status == 'INVALID':
                messages = [t.get('message', '') for t in batch_status.get('invalid_transactions', [])]
                raise CaException('Transaction rejected: {}'.format('; '.join(messages) or 'unknown reason'))
            if status != 'PENDING' or time.time() >= deadline:
                return status

    def _create_batch_list(self, transactions):
        transaction_signatures = [t.header_signature for t in transactions]

        header = BatchHeader(
            signer_public_key=self.public_key,
            transaction_ids=transaction_signatures
        ).SerializeToString()

        signature = self._signer.sign(header)

        batch = Batch(
            header=header,
            transactions=transactions,
            header_signature=signature)
        return BatchList(batches=[batch])


def get_simple_address(data):
    prefix = _sha512('simple'.encode('utf-8'))[:6]
    address = _sha512(data.encode('utf-8'))[:64]
    return prefix + address


def _error_message(response):
    try:
        return response.json()['error']['message']
    except (ValueError, KeyError, TypeError):
        return response.reason
