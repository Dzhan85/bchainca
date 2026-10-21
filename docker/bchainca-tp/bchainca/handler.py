import logging

from sawtooth_sdk.processor.exceptions import InvalidTransaction, InternalError
from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.protobuf.processor_pb2 import TpProcessRequest

from CaPayload import CaPayload
from CaState import CaState

LOGGER = logging.getLogger(__name__)


class CAHandler(TransactionHandler):

    def __init__(self, namespace_prefix):
        self._namespace_prefix = namespace_prefix

    @property
    def family_name(self):
        return 'CA'

    @property
    def namespaces(self):
        return [self._namespace_prefix]

    @property
    def family_versions(self):
        return ['1.0']

    def apply(self, transaction: TpProcessRequest, context):

        header = transaction.header
        signer = header.signer_public_key
        try:
            state = CaState(context=context, namespace=self._namespace_prefix, timeout=2)
            # state.check_CA_cert()
            payload = CaPayload(payload=transaction.payload)
            nonce = int(header.nonce, 0)

            if payload.action == 'init':
                state.init_CA_cert(date=payload.date, nonce=nonce, spkey=payload.value, admin=signer)
            elif payload.action == 'create':
                cert_bytes = state.create_certificate(date=payload.date, nonce=nonce, csr=payload.value,
                                                      owner=signer)
                self._fire_event(context, 'create', nonce, cert_bytes)
            elif payload.action == 'get':
                cert_bytes = state.get_certificate(payload.serial)
                self._fire_event(context, 'get', payload.serial, cert_bytes)
            elif payload.action == 'revoke':
                state.revoke_certificate(payload.serial, signer=signer, date=payload.date)
                self._fire_event(context, 'revoke', payload.serial)
            elif payload.action == 'status':
                status = state.check_status(payload.serial, date=payload.date)
                self._fire_event(context, 'status', payload.serial, status.encode('utf-8'))
            else:
                raise InvalidTransaction("Transaction payload type unknown.")
        except InvalidTransaction:
            raise
        except InternalError as er:
            raise InvalidTransaction(str(er)) from er
        except Exception as ex:
            raise InvalidTransaction(str(ex)) from ex

    def _fire_event(self, context, action, serial, data=b''):
        event_name = "{}/{}".format(self._namespace_prefix, action)
        LOGGER.debug("fire event " + event_name)
        # The serial is always sent in decimal, matching the state key and
        # the serial number embedded in the certificate.
        context.add_event(event_name, [("serial", str(serial))], data)


def _display(msg):
    n = msg.count("\n")

    if n > 0:
        msg = msg.split("\n")
        length = max(len(line) for line in msg)
    else:
        length = len(msg)
        msg = [msg]

    LOGGER.debug("+" + (length + 2) * "-" + "+")
    for line in msg:
        LOGGER.debug("+ " + line.center(length) + " +")
    LOGGER.debug("+" + (length + 2) * "-" + "+")
