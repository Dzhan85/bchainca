import datetime
import hashlib
import json
import logging

from sawtooth_sdk.processor.exceptions import InternalError
from certgen import *

LOGGER = logging.getLogger(__name__)

# NOTE: this module runs inside the transaction processor container
# (Python 3.5), so it must not use f-strings or other newer syntax.

# The CA private key is stored PEM-encrypted with this passphrase. It must
# match CA_KEY_PASSPHRASE in bchainca-cli/client.py.
CA_KEY_PASSPHRASE = b'passw'

CA_VALIDITY = datetime.timedelta(days=3650)
CERT_VALIDITY = datetime.timedelta(days=365)

CA_ROOT_ENTITY = 'CA_Root'
CA_PKEY_ENTITY = 'CA_PKey'
CA_ADMIN_ENTITY = 'CA_Admin'

STATE_VALID = 'Valid'
STATE_REVOKED = 'Revoked'
STATE_EXPIRED = 'Expired'


# WARNING: Using JSON instead of pickle for security
# Pickle can execute arbitrary code and is unsafe for untrusted data
def _serialize(obj):
    """Serialize Certificate object to JSON bytes (secure alternative to pickle)."""
    if isinstance(obj, Certificate):
        data = {
            'state': obj.state,
            'valid_till_timestamp': obj.valid_till_timestamp,
            'revoke_timestamp': obj.revoke_timestamp,
            'serial_number': str(obj.serial_number),
            'certificate_string': obj.certificate_string.decode('utf-8'),
            'subject_name': str(obj.subject_name),
            'owner': obj.owner,
        }
        return json.dumps(data, sort_keys=True).encode('utf-8')
    raise TypeError("Cannot serialize object of type {}".format(type(obj)))


def _deserialize(data):
    """Deserialize JSON bytes to Certificate object (secure alternative to pickle)."""
    if data is None:
        return None
    try:
        obj_dict = json.loads(data.decode('utf-8'))
        return Certificate(
            state=obj_dict['state'],
            valid_till_timestamp=obj_dict['valid_till_timestamp'],
            revoke_timestamp=obj_dict['revoke_timestamp'],
            serial_number=int(obj_dict['serial_number']),
            certificate_string=obj_dict['certificate_string'].encode('utf-8'),
            subject_name=obj_dict['subject_name'],
            owner=obj_dict.get('owner')
        )
    except (ValueError, KeyError) as e:  # json.JSONDecodeError is a ValueError
        LOGGER.error("Failed to deserialize certificate data: {}".format(e))
        raise InternalError("Invalid certificate data: {}".format(e))


class Certificate:
    def __init__(self,
                 state,
                 valid_till_timestamp,
                 revoke_timestamp,
                 serial_number,
                 certificate_string,
                 subject_name,
                 owner=None):
        """Constructor.
        Args:
            state (str): Certificate state. 'Valid' or 'Revoked'.
            valid_till_timestamp (int): Certificate valid till timestamp.
            revoke_timestamp (int): Certificate revoke timestamp, 0 if not revoked.
            serial_number (int): Certificate serial number.
            certificate_string (bytes): PEM encoded certificate.
            subject_name (str): Certificate subject name.
            owner (str): Public key of the transaction signer that requested
                the certificate. None for certificates created before
                ownership was tracked.
        """

        self._state = state
        self._valid_till_timestamp = valid_till_timestamp
        self._revoke_timestamp = revoke_timestamp
        self._serial_number = serial_number
        self._certificate_string = certificate_string
        self._subject_name = subject_name
        self._owner = owner

    @classmethod
    def from_cert(cls, state, cert, owner):
        return cls(state=state,
                   valid_till_timestamp=utc_timestamp(not_valid_after(cert)),
                   revoke_timestamp=0,
                   serial_number=cert.serial_number,
                   certificate_string=serialize_certificate(cert),
                   subject_name=subject_to_string(cert.subject),
                   owner=owner)

    @property
    def state(self):
        """Certificate state.
        :return: str, 'Valid' or 'Revoked'.
        """
        return self._state

    @property
    def valid_till_timestamp(self):
        """Certificate valid till timestamp.
        :return: int, timestamp.
        """
        return self._valid_till_timestamp

    @property
    def revoke_timestamp(self):
        """Certificate revoke timestamp.
        :return: int, timestamp.
        """
        return self._revoke_timestamp

    @property
    def serial_number(self):
        """Certificate serial number.
        :return: int, serial number.
        """
        return self._serial_number

    @property
    def certificate_string(self):
        """PEM encoded certificate.
        :return: bytes.
        """
        return self._certificate_string

    @property
    def subject_name(self):
        """Certificate subject name.
        :return: str, Certificate subject name.
        """
        return self._subject_name

    @property
    def owner(self):
        """Public key of the certificate requester.
        :return: str or None.
        """
        return self._owner

    def status_at(self, timestamp):
        """State of the certificate at the given POSIX timestamp."""
        if self._state == STATE_VALID and timestamp > self._valid_till_timestamp:
            return STATE_EXPIRED
        return self._state

    def revoke(self, timestamp):
        self._state = STATE_REVOKED
        self._revoke_timestamp = timestamp


class CaState:
    def __init__(self, context, namespace, timeout):
        """Constructor.
        Args:
            context (sawtooth_sdk.processor.context.Context): Access to
                validator state from within the transaction processor.
            timeout (int): Timeout in seconds.
        """

        self._context = context
        self._address_cache = {}
        self._timeout = int(timeout)
        self._namespace = namespace

    def _generate_address(self, entity):
        if not isinstance(entity, bytes):
            entity = entity.encode('utf-8')
        return hashlib.sha512(self._namespace.encode('utf-8')).hexdigest()[:6] + \
            hashlib.sha512(entity).hexdigest()[:64]

    def init_CA_cert(self, date, nonce, spkey, admin):
        """Create the self-signed CA root certificate.

        Args:
            date (datetime): Transaction date, used as the start of validity.
            nonce (int): Transaction nonce, used as the certificate serial.
            spkey (bytes): PEM encoded, CA_KEY_PASSPHRASE encrypted CA key.
            admin (str): Public key of the signer, who becomes the CA admin
                and may revoke any certificate.
        """
        if self._load_entity_state(CA_ROOT_ENTITY) is not None:
            raise InternalError("CA is already initialized")

        pkey = deserialize_pkey(spkey, CA_KEY_PASSPHRASE)
        csr = create_cert_request(pkey,
                                  C=u'RU',
                                  ST=u'Tatarstan',
                                  L=u'Innopolis',
                                  O=u'SNE',
                                  CN=u'demo CA',
                                  emailAddress=u'v.osmov@innopolis.ru')
        cert = create_certificate(
            request=csr,
            issuer_cert=csr,
            issuer_key=pkey,
            not_before=date,
            not_after=date + CA_VALIDITY,
            serial=nonce,
            is_ca=True)
        self._save_entity_state(CA_PKEY_ENTITY, spkey)
        data = serialize_certificate(cert)
        LOGGER.debug("Write data: [{}] => {}".format(CA_ROOT_ENTITY, data))
        self._save_entity_state(CA_ROOT_ENTITY, data)
        self._save_entity_state(CA_ADMIN_ENTITY, admin.encode('utf-8'))

    def _load_CA_cert(self):
        data = self._load_entity_state(CA_ROOT_ENTITY)
        if data is None:
            raise InternalError("CA Root certificate not found. Init first")
        return deserialize_certificate(data)

    def _load_CA_pkey(self):
        data = self._load_entity_state(CA_PKEY_ENTITY)
        if data is None:
            raise InternalError("CA keys not found. Init first")
        return deserialize_pkey(data, CA_KEY_PASSPHRASE)

    def _load_CA_admin(self):
        data = self._load_entity_state(CA_ADMIN_ENTITY)
        return data.decode('utf-8') if data is not None else None

    def _save_entity_state(self, entity, data):
        address = self._generate_address(entity)
        self._address_cache[address] = data
        self._context.set_state(
            {address: data},
            timeout=self._timeout)

    def _load_entity_state(self, entity):
        address = self._generate_address(entity)
        data = None
        if address in self._address_cache:
            if self._address_cache[address]:
                data = self._address_cache[address]
        else:
            state_entries = self._context.get_state(
                [address],
                timeout=self._timeout)
            if state_entries:
                self._address_cache[address] = state_entries[0].data
                data = state_entries[0].data
            else:
                self._address_cache[address] = None
        return data

    def _load_certificate(self, serial):
        obj = _deserialize(self._load_entity_state(entity=str(serial)))
        if obj is None:
            raise InternalError("Certificate {} not found".format(serial))
        return obj

    def create_certificate(self, date, nonce, csr, owner):
        """Issue a certificate for the CSR, using the nonce as serial number.

        Returns:
            bytes: PEM encoded certificate.
        """
        if self._load_entity_state(entity=str(nonce)) is not None:
            raise InternalError("Certificate with serial {} already exists".format(nonce))

        ca_cert = self._load_CA_cert()
        ca_pkey = self._load_CA_pkey()
        cert = create_certificate(
            request=x509.load_pem_x509_csr(csr, default_backend()),
            issuer_cert=ca_cert,
            issuer_key=ca_pkey,
            not_before=date,
            not_after=date + CERT_VALIDITY,
            serial=nonce)
        obj = Certificate.from_cert(state=STATE_VALID, cert=cert, owner=owner)
        self._save_entity_state(entity=str(cert.serial_number),
                                data=_serialize(obj))
        return obj.certificate_string

    def get_certificate(self, serial):
        return self._load_certificate(serial).certificate_string

    def revoke_certificate(self, serial, signer, date):
        """Revoke a certificate. Only its owner or the CA admin may do so."""
        obj = self._load_certificate(serial)
        if signer not in (obj.owner, self._load_CA_admin()):
            raise InternalError("Signer is not allowed to revoke certificate {}".format(serial))
        if obj.state == STATE_REVOKED:
            raise InternalError("Certificate {} is already revoked".format(serial))
        obj.revoke(utc_timestamp(date))
        self._save_entity_state(entity=str(obj.serial_number),
                                data=_serialize(obj))

    def check_status(self, serial, date):
        return self._load_certificate(serial).status_at(utc_timestamp(date))
