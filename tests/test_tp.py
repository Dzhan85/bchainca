import datetime
import json
import os
import time
from types import SimpleNamespace

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import serialization

from sawtooth_sdk.processor.exceptions import InvalidTransaction

import cli
import client
from CaPayload import CaPayload
from conftest import FakeContext
from handler import CAHandler

ADMIN = 'admin-public-key'
ALICE = 'alice-public-key'
BOB = 'bob-public-key'
DATE = datetime.datetime(2026, 1, 1, 12, 0, 0)


@pytest.fixture(scope='module')
def ca_key_pem():
    key = cli.create_key_pair()
    return key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.BestAvailableEncryption(client.CA_KEY_PASSPHRASE)).decode()


@pytest.fixture(scope='module')
def csr_pem():
    csr = cli.create_cert_request(cli.create_key_pair(), C='RU', O='SNE', CN='alice@example.com')
    return csr.public_bytes(serialization.Encoding.PEM).decode()


def apply(context, action, value, signer, nonce=1, date=DATE):
    request = SimpleNamespace(
        header=SimpleNamespace(signer_public_key=signer, nonce=hex(nonce)),
        payload=client.make_payload(action, value, date))
    CAHandler(client.NAMESPACE).apply(request, context)


def record(context, serial):
    return json.loads(context.state[client.get_address(serial)].decode())


@pytest.fixture
def ca(context, ca_key_pem):
    apply(context, 'init', ca_key_pem, ADMIN, nonce=1)
    return context


def test_init_stores_ca_root_and_admin(ca):
    root = x509.load_pem_x509_certificate(ca.state[client.get_address(client.CA_ROOT_ENTITY)])
    assert root.extensions.get_extension_for_class(x509.BasicConstraints).value.ca is True
    assert root.not_valid_after_utc - root.not_valid_before_utc == datetime.timedelta(days=3650)
    assert ca.state[client.get_address(client.CA_ADMIN_ENTITY)] == ADMIN.encode()


def test_init_twice_is_rejected(ca, ca_key_pem):
    with pytest.raises(InvalidTransaction, match='already initialized'):
        apply(ca, 'init', ca_key_pem, ADMIN, nonce=2)


def test_create_requires_init(context, csr_pem):
    with pytest.raises(InvalidTransaction, match='Init first'):
        apply(context, 'create', csr_pem, ALICE, nonce=42)


def test_create_issues_leaf_certificate_signed_by_ca(ca, csr_pem):
    apply(ca, 'create', csr_pem, ALICE, nonce=42)

    stored = record(ca, 42)
    assert stored['state'] == 'Valid'
    assert stored['owner'] == ALICE
    assert 'CN=alice@example.com' in stored['subject_name']

    cert = x509.load_pem_x509_certificate(stored['certificate_string'].encode())
    root = x509.load_pem_x509_certificate(ca.state[client.get_address(client.CA_ROOT_ENTITY)])
    cert.verify_directly_issued_by(root)
    assert cert.serial_number == 42
    assert cert.extensions.get_extension_for_class(x509.BasicConstraints).value.ca is False
    assert cert.not_valid_after_utc - cert.not_valid_before_utc == datetime.timedelta(days=365)

    event = ca.events[-1]
    assert event.event_type == 'ca_1/create'
    assert event.attributes == [('serial', '42')]
    assert event.data == stored['certificate_string'].encode()


def test_create_with_existing_serial_is_rejected(ca, csr_pem):
    apply(ca, 'create', csr_pem, ALICE, nonce=42)
    with pytest.raises(InvalidTransaction, match='already exists'):
        apply(ca, 'create', csr_pem, BOB, nonce=42)
    assert record(ca, 42)['owner'] == ALICE


def test_state_does_not_depend_on_validator_time_zone(ca_key_pem, csr_pem):
    """Every validator must write byte-identical state, whatever its TZ."""
    if not hasattr(time, 'tzset'):
        pytest.skip('time.tzset is not available on this platform')

    states = []
    original_tz = os.environ.get('TZ')
    try:
        for tz in ('UTC', 'Asia/Tokyo'):
            os.environ['TZ'] = tz
            time.tzset()
            context = FakeContext()
            apply(context, 'init', ca_key_pem, ADMIN, nonce=1)
            apply(context, 'create', csr_pem, ALICE, nonce=42)
            states.append(context.state)
    finally:
        if original_tz is None:
            os.environ.pop('TZ', None)
        else:
            os.environ['TZ'] = original_tz
        time.tzset()

    assert states[0] == states[1]


def test_owner_can_revoke(ca, csr_pem):
    apply(ca, 'create', csr_pem, ALICE, nonce=42)
    revoke_date = DATE + datetime.timedelta(days=1)
    apply(ca, 'revoke', 42, ALICE, nonce=43, date=revoke_date)

    stored = record(ca, 42)
    assert stored['state'] == 'Revoked'
    assert stored['revoke_timestamp'] == int(revoke_date.replace(tzinfo=datetime.timezone.utc).timestamp())
    assert ca.events[-1].event_type == 'ca_1/revoke'


def test_admin_can_revoke_any_certificate(ca, csr_pem):
    apply(ca, 'create', csr_pem, ALICE, nonce=42)
    apply(ca, 'revoke', 42, ADMIN, nonce=43)
    assert record(ca, 42)['state'] == 'Revoked'


def test_other_signer_cannot_revoke(ca, csr_pem):
    apply(ca, 'create', csr_pem, ALICE, nonce=42)
    with pytest.raises(InvalidTransaction, match='not allowed'):
        apply(ca, 'revoke', 42, BOB, nonce=43)
    assert record(ca, 42)['state'] == 'Valid'


def test_revoking_twice_is_rejected(ca, csr_pem):
    apply(ca, 'create', csr_pem, ALICE, nonce=42)
    apply(ca, 'revoke', 42, ALICE, nonce=43)
    with pytest.raises(InvalidTransaction, match='already revoked'):
        apply(ca, 'revoke', 42, ALICE, nonce=44)


@pytest.mark.parametrize('action', ['get', 'status', 'revoke'])
def test_unknown_serial_is_reported(ca, action):
    with pytest.raises(InvalidTransaction, match='Certificate 999 not found'):
        apply(ca, action, 999, ALICE, nonce=43)


def test_status_reports_expired_after_validity(ca, csr_pem):
    apply(ca, 'create', csr_pem, ALICE, nonce=42)
    apply(ca, 'status', 42, ALICE, nonce=43, date=DATE + datetime.timedelta(days=30))
    assert ca.events[-1].data == b'Valid'
    apply(ca, 'status', 42, ALICE, nonce=44, date=DATE + datetime.timedelta(days=366))
    assert ca.events[-1].data == b'Expired'


def test_get_fires_event_with_certificate(ca, csr_pem):
    apply(ca, 'create', csr_pem, ALICE, nonce=42)
    apply(ca, 'get', 42, BOB, nonce=43)
    assert ca.events[-1].event_type == 'ca_1/get'
    assert ca.events[-1].data == record(ca, 42)['certificate_string'].encode()


@pytest.mark.parametrize('payload, message', [
    (b'create|2026-01-01T00:00:00', 'Malformed payload'),
    (b'\xff\xfe', 'Malformed payload'),
    (b'delete|2026-01-01T00:00:00|1', 'Invalid action'),
    (b'revoke|2026-01-01T00:00:00|abc', 'Invalid serial'),
    (b'revoke|not-a-date|1', 'Invalid date'),
])
def test_invalid_payloads_are_rejected(payload, message):
    with pytest.raises(InvalidTransaction, match=message):
        CaPayload(payload)


def test_payload_value_may_contain_delimiter():
    payload = CaPayload(b'create|2026-01-01T00:00:00|a|b')
    assert payload.value == b'a|b'
