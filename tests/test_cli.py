import os
import re
import stat
from unittest import mock

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.x509.oid import NameOID

import cli
import client
from CaException import CaException
from CaState import CaState


def run(capsys, *args):
    cli.main(prog_name='bchainca', args=list(args))
    return capsys.readouterr().out


def signing_args(key_dir, user):
    return ['--key-dir', str(key_dir), '--username', user]


def create(capsys, key_dir, out_dir, user='alice', name='alice@example.com'):
    out = run(capsys, 'create', name, '--out-dir', str(out_dir), *signing_args(key_dir, user))
    return re.search(r'Serial: (\d+)', out).group(1)


@pytest.fixture
def initialized(ledger, key_dir, capsys):
    run(capsys, 'init', '--key-size', '1024', *signing_args(key_dir, 'admin'))
    return ledger


def test_address_matches_transaction_processor():
    state = CaState(context=None, namespace=client.NAMESPACE, timeout=1)
    for entity in ('CA_Root', '1234567890'):
        assert client.get_address(entity) == state._generate_address(entity)


def test_keyfile_honours_key_dir(tmp_path):
    args = cli.create_parser('bchainca').parse_args(
        ['create', 'x', '--key-dir', str(tmp_path), '--username', 'carol'])
    assert cli._get_keyfile(args) == os.path.join(str(tmp_path), 'carol.priv')


def test_serial_must_be_decimal():
    with pytest.raises(SystemExit):
        cli.create_parser('bchainca').parse_args(['status', '0xff'])


def test_cert_request_omits_missing_attributes():
    csr = cli.create_cert_request(cli.create_key_pair(1024), CN='host', O=None, C='')
    assert [a.oid for a in csr.subject] == [NameOID.COMMON_NAME]


def test_cert_request_rejects_invalid_country():
    with pytest.raises(CaException, match='Invalid subject'):
        cli.create_cert_request(cli.create_key_pair(1024), C='RUS', CN='host')


def test_init_reports_admin(ledger, key_dir, capsys):
    out = run(capsys, 'init', '--key-size', '1024', *signing_args(key_dir, 'admin'))
    assert 'CA initialized' in out


def test_init_twice_fails(initialized, key_dir, capsys):
    with pytest.raises(CaException, match='already initialized'):
        run(capsys, 'init', '--key-size', '1024', *signing_args(key_dir, 'admin'))


def test_create_saves_certificate_and_private_key(initialized, key_dir, tmp_path, capsys):
    serial = create(capsys, key_dir, tmp_path / 'out')

    key_file = tmp_path / 'out' / 'cert_{}.key'.format(serial)
    cert_file = tmp_path / 'out' / 'cert_{}.pem'.format(serial)
    assert stat.S_IMODE(key_file.stat().st_mode) == 0o600

    cert = x509.load_pem_x509_certificate(cert_file.read_bytes())
    key = serialization.load_pem_private_key(key_file.read_bytes(), password=None)
    assert cert.public_key().public_numbers() == key.public_key().public_numbers()
    assert str(cert.serial_number) == serial
    assert cert.subject.get_attributes_for_oid(NameOID.EMAIL_ADDRESS)[0].value == 'alice@example.com'


def test_create_with_encrypted_key(initialized, key_dir, tmp_path, capsys):
    with mock.patch('getpass.getpass', return_value='s3cret'):
        out = run(capsys, 'create', 'host', '--encrypt-key', '--out-dir', str(tmp_path),
                  *signing_args(key_dir, 'alice'))
    serial = re.search(r'Serial: (\d+)', out).group(1)
    data = (tmp_path / 'cert_{}.key'.format(serial)).read_bytes()
    serialization.load_pem_private_key(data, password=b's3cret')


def test_create_before_init_fails(ledger, key_dir, tmp_path, capsys):
    with pytest.raises(CaException, match='Init first'):
        create(capsys, key_dir, tmp_path)


def test_status_list_and_get(initialized, key_dir, tmp_path, capsys):
    serial = create(capsys, key_dir, tmp_path)

    out = run(capsys, 'status', serial)
    assert 'Status     : Valid' in out
    assert 'Owner      : unknown' not in out

    out = run(capsys, 'list')
    assert serial in out and 'CN=alice@example.com' in out
    # The CA root certificate, key and admin entries are not listed.
    assert len(out.strip().splitlines()) == 2

    output = tmp_path / 'downloaded.pem'
    run(capsys, 'get', serial, '-o', str(output))
    assert output.read_bytes() == (tmp_path / 'cert_{}.pem'.format(serial)).read_bytes()


def test_unknown_serial(initialized, capsys):
    with pytest.raises(CaException, match='not found'):
        run(capsys, 'status', '12345')


def test_list_empty(ledger, capsys):
    assert 'No certificates found' in run(capsys, 'list')


def test_verify_valid_then_revoked(initialized, key_dir, tmp_path, capsys):
    serial = create(capsys, key_dir, tmp_path)
    cert_file = str(tmp_path / 'cert_{}.pem'.format(serial))

    assert 'OK' in run(capsys, 'verify', cert_file)

    run(capsys, 'revoke', serial, *signing_args(key_dir, 'alice'))
    assert 'Status     : Revoked' in run(capsys, 'status', serial)

    with pytest.raises(SystemExit) as exit_info:
        run(capsys, 'verify', cert_file)
    assert exit_info.value.code == 1
    assert 'certificate is revoked' in capsys.readouterr().out


def test_verify_rejects_certificate_from_another_ca(initialized, tmp_path, capsys):
    other_key = cli.create_key_pair(1024)
    csr = cli.create_cert_request(other_key, CN='forged')
    forged = x509.CertificateBuilder() \
        .subject_name(csr.subject).issuer_name(csr.subject).public_key(other_key.public_key()) \
        .serial_number(7).not_valid_before(cli.datetime.datetime(2026, 1, 1)) \
        .not_valid_after(cli.datetime.datetime(2036, 1, 1)) \
        .sign(other_key, cli.hashes.SHA256())
    path = tmp_path / 'forged.pem'
    path.write_bytes(forged.public_bytes(serialization.Encoding.PEM))

    with pytest.raises(SystemExit):
        run(capsys, 'verify', str(path))
    out = capsys.readouterr().out
    assert 'not issued by the CA root' in out
    assert 'not on the ledger' in out


def test_only_owner_or_admin_can_revoke(initialized, key_dir, tmp_path, capsys):
    serial = create(capsys, key_dir, tmp_path)
    with pytest.raises(CaException, match='not allowed'):
        run(capsys, 'revoke', serial, *signing_args(key_dir, 'bob'))
    run(capsys, 'revoke', serial, *signing_args(key_dir, 'admin'))


def test_ca_cert_download(initialized, tmp_path, capsys):
    output = tmp_path / 'ca.pem'
    run(capsys, 'ca-cert', '-o', str(output))
    root = x509.load_pem_x509_certificate(output.read_bytes())
    assert root.extensions.get_extension_for_class(x509.BasicConstraints).value.ca is True


def test_record_status_reports_expired():
    record = {'state': 'Valid', 'valid_till_timestamp': 100}
    assert cli.record_status(record, now=50) == 'Valid'
    assert cli.record_status(record, now=150) == 'Expired'
    assert cli.record_status(dict(record, state='Revoked'), now=150) == 'Revoked'


class FakeResponse:
    def __init__(self, status_code=200, body=None):
        self.status_code = status_code
        self.ok = status_code < 400
        self.reason = 'reason'
        self._body = body if body is not None else {}

    def json(self):
        return self._body


def make_client(key_dir):
    return client.CaClient('localhost:8008', keyfile=str(key_dir / 'alice.priv'))


def test_submit_reports_invalid_transaction(key_dir):
    status = {'data': [{'status': 'INVALID', 'invalid_transactions': [{'message': 'Signer is not allowed'}]}]}
    with mock.patch('requests.post', return_value=FakeResponse(202)), \
            mock.patch('requests.get', return_value=FakeResponse(200, status)):
        with pytest.raises(CaException, match='Transaction rejected: Signer is not allowed'):
            make_client(key_dir).revoke('1', wait=5)


def test_submit_without_wait_does_not_poll(key_dir):
    with mock.patch('requests.post', return_value=FakeResponse(202)) as post, \
            mock.patch('requests.get') as get:
        serial, status = make_client(key_dir).revoke('1', wait=0)
    assert status == 'SUBMITTED'
    assert post.call_args[0][0] == 'http://localhost:8008/batches'
    get.assert_not_called()


def test_list_records_follows_paging_and_skips_non_certificates(key_dir):
    import base64
    import json

    def entry(data):
        return {'data': base64.b64encode(data).decode()}

    pages = {
        'http://localhost:8008/state?address={}'.format(client.get_prefix()): FakeResponse(200, {
            'data': [entry(b'-----BEGIN CERTIFICATE-----'), entry(json.dumps({'serial_number': '9'}).encode())],
            'paging': {'next': 'http://localhost:8008/state?address=x&start=2'}}),
        'http://localhost:8008/state?address=x&start=2': FakeResponse(200, {
            'data': [entry(json.dumps({'serial_number': '3'}).encode())], 'paging': {}}),
    }
    with mock.patch('requests.get', side_effect=lambda url, **kw: pages[url]):
        records = make_client(key_dir).list_records()
    assert [r['serial_number'] for r in records] == ['3', '9']


def test_missing_state_returns_none(key_dir):
    with mock.patch('requests.get', return_value=FakeResponse(404)):
        assert make_client(key_dir).get_record('1') is None


def test_rest_api_error_message(key_dir):
    body = {'error': {'message': 'Validator is not ready'}}
    with mock.patch('requests.get', return_value=FakeResponse(503, body)):
        with pytest.raises(CaException, match='Error 503: Validator is not ready'):
            make_client(key_dir).get_ca_certificate()


def test_new_serial_is_positive_and_fits_63_bits():
    serials = {client.new_serial() for _ in range(100)}
    assert all(0 < s < 2 ** 63 for s in serials)
    assert len(serials) == 100

