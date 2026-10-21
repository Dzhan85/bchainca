"""Test setup for the CA transaction processor and bchainca-cli.

The Sawtooth SDK only installs on older Python versions (its secp256k1
dependency fails to build on newer ones), so when it is missing we register
minimal stand-ins for the handful of names the code imports. When the real
SDK is installed it is used instead.
"""
import base64
import hashlib
import json
import os
import sys
import types
from types import SimpleNamespace

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'bchainca-cli'))
sys.path.insert(0, os.path.join(ROOT, 'docker', 'bchainca-tp', 'bchainca'))


def _module(name, **attrs):
    module = types.ModuleType(name)
    module.__dict__.update(attrs)
    sys.modules[name] = module
    return module


class _FakeMessage:
    """Stand-in for a protobuf message: keyword fields, JSON wire format."""

    def __init__(self, **fields):
        self.__dict__.update(fields)

    def SerializeToString(self):
        def encode(value):
            if isinstance(value, bytes):
                return {'__bytes__': base64.b64encode(value).decode()}
            if isinstance(value, _FakeMessage):
                return {k: encode(v) for k, v in value.__dict__.items()}
            if isinstance(value, list):
                return [encode(v) for v in value]
            return value
        return json.dumps(encode(self), sort_keys=True).encode()

    def ParseFromString(self, data):
        self.__dict__.update(json.loads(data.decode()))


def _install_sawtooth_stubs():
    class InvalidTransaction(Exception):
        pass

    class InternalError(Exception):
        pass

    class ParseError(Exception):
        pass

    class Secp256k1PrivateKey:
        def __init__(self, key_hex):
            self.key_hex = key_hex

        @classmethod
        def from_hex(cls, key_hex):
            if not key_hex:
                raise ParseError('empty key')
            return cls(key_hex)

    class _Signer:
        def __init__(self, private_key):
            self._public = 'pub-' + private_key.key_hex

        def get_public_key(self):
            return SimpleNamespace(as_hex=lambda: self._public)

        def sign(self, data):
            return hashlib.sha256(self._public.encode() + data).hexdigest()

    class CryptoFactory:
        def __init__(self, context):
            pass

        def new_signer(self, private_key):
            return _Signer(private_key)

    message_types = {name: type(name, (_FakeMessage,), {})
                     for name in ('TransactionHeader', 'Transaction', 'BatchList',
                                  'BatchHeader', 'Batch', 'TpProcessRequest')}

    _module('sawtooth_sdk')
    _module('sawtooth_sdk.processor')
    _module('sawtooth_sdk.processor.exceptions',
            InvalidTransaction=InvalidTransaction, InternalError=InternalError)
    _module('sawtooth_sdk.processor.handler', TransactionHandler=object)
    _module('sawtooth_sdk.protobuf')
    _module('sawtooth_sdk.protobuf.processor_pb2', TpProcessRequest=message_types['TpProcessRequest'])
    _module('sawtooth_sdk.protobuf.transaction_pb2',
            TransactionHeader=message_types['TransactionHeader'],
            Transaction=message_types['Transaction'])
    _module('sawtooth_sdk.protobuf.batch_pb2',
            BatchList=message_types['BatchList'],
            BatchHeader=message_types['BatchHeader'],
            Batch=message_types['Batch'])
    _module('sawtooth_signing', create_context=lambda name: name,
            CryptoFactory=CryptoFactory, ParseError=ParseError)
    _module('sawtooth_signing.secp256k1', Secp256k1PrivateKey=Secp256k1PrivateKey)


try:
    import sawtooth_sdk.processor.exceptions  # noqa: F401
    import sawtooth_signing  # noqa: F401
except ImportError:
    _install_sawtooth_stubs()


class FakeContext:
    """In-memory stand-in for the validator context given to a handler."""

    def __init__(self):
        self.state = {}
        self.events = []

    def get_state(self, addresses, timeout=None):
        return [SimpleNamespace(address=a, data=self.state[a]) for a in addresses if a in self.state]

    def set_state(self, entries, timeout=None):
        self.state.update(entries)
        return list(entries)

    def add_event(self, event_type, attributes=None, data=None, timeout=None):
        self.events.append(SimpleNamespace(event_type=event_type, attributes=attributes or [], data=data))


@pytest.fixture
def context():
    return FakeContext()


@pytest.fixture
def ledger(monkeypatch, context):
    """Route CaClient transactions and state reads through the real CA handler.

    Returns the FakeContext holding global state.
    """
    from sawtooth_sdk.processor.exceptions import InvalidTransaction
    from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader

    import client as client_module
    from CaException import CaException
    from handler import CAHandler

    handler = CAHandler(client_module.NAMESPACE)

    def submit(self, transactions, wait, auth_user, auth_password):
        for txn in transactions:
            header = TransactionHeader()
            header.ParseFromString(txn.header)
            try:
                handler.apply(SimpleNamespace(header=header, payload=txn.payload), context)
            except InvalidTransaction as err:
                raise CaException('Transaction rejected: {}'.format(err))
        return 'COMMITTED'

    def get_state(self, address, auth_user=None, auth_password=None):
        return context.state.get(address)

    def list_state(self, prefix, auth_user=None, auth_password=None):
        for address, data in sorted(context.state.items()):
            if address.startswith(prefix):
                yield {'address': address, 'data': base64.b64encode(data).decode()}

    monkeypatch.setattr(client_module.CaClient, '_submit', submit)
    monkeypatch.setattr(client_module.CaClient, '_get_state', get_state)
    monkeypatch.setattr(client_module.CaClient, '_list_state', list_state)
    return context


@pytest.fixture
def key_dir(tmp_path):
    """Directory with private key files for users 'admin', 'alice' and 'bob'."""
    directory = tmp_path / 'keys'
    directory.mkdir()
    for user, key in (('admin', '01' * 32), ('alice', '02' * 32), ('bob', '03' * 32)):
        (directory / '{}.priv'.format(user)).write_text(key)
    return directory
