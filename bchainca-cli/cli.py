from __future__ import print_function

import argparse
import datetime
import getpass
import logging
import os
import traceback
import sys

from colorlog import ColoredFormatter
from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from client import CaClient, CA_KEY_PASSPHRASE
from CaException import CaException


DISTRIBUTION_NAME = 'sawtooth-ca'


DEFAULT_URL = 'http://127.0.0.1:8008'

# Seconds to wait for a transaction to commit. Issuing a certificate needs
# the commit to complete, so unlike the XO example this is on by default.
DEFAULT_WAIT = 60

LOGGER = logging.getLogger(__name__)


def create_console_handler(verbose_level):
    clog = logging.StreamHandler()
    formatter = ColoredFormatter(
        "%(log_color)s[%(asctime)s %(levelname)-8s%(module)s]%(reset)s "
        "%(white)s%(message)s",
        datefmt="%H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        })

    clog.setFormatter(formatter)

    if verbose_level == 0:
        clog.setLevel(logging.WARN)
    elif verbose_level == 1:
        clog.setLevel(logging.INFO)
    else:
        clog.setLevel(logging.DEBUG)

    return clog


def setup_loggers(verbose_level):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(create_console_handler(verbose_level))


def create_parent_parser(prog_name):
    parent_parser = argparse.ArgumentParser(prog=prog_name, add_help=False)
    parent_parser.add_argument(
        '-v', '--verbose',
        action='count',
        help='enable more verbose output')

    parent_parser.add_argument(
        '-V', '--version',
        action='version',
        version=(DISTRIBUTION_NAME + ' (Hyperledger Sawtooth) version {}')
        .format(_get_version()),
        help='display version information')

    return parent_parser


def create_rest_parser():
    """Options shared by every subcommand that talks to the REST API."""
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API (default: {})'.format(DEFAULT_URL))

    parser.add_argument(
        '--auth-user',
        type=str,
        help='specify username for authentication if REST API '
        'is using Basic Auth')

    parser.add_argument(
        '--auth-password',
        type=str,
        help='specify password for authentication if REST API '
        'is using Basic Auth')

    return parser


def create_signing_parser():
    """Options shared by every subcommand that submits a transaction."""
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument(
        '--username',
        type=str,
        help="identify name of user's private key file")

    parser.add_argument(
        '--key-dir',
        type=str,
        help="identify directory of user's private key file "
        "(default: ~/.sawtooth/keys)")

    parser.add_argument(
        '--wait',
        type=int,
        default=DEFAULT_WAIT,
        help='set time, in seconds, to wait for the transaction to commit '
        '(default: {})'.format(DEFAULT_WAIT))

    return parser


def create_parser(prog_name):
    parent_parser = create_parent_parser(prog_name)
    rest = create_rest_parser()
    signing = create_signing_parser()

    parser = argparse.ArgumentParser(
        description='Blockchain certificate authority on Hyperledger '
        'Sawtooth. Issues, revokes and verifies X.509 certificates by '
        'sending CA transactions and reading global state.',
        parents=[parent_parser])

    subparsers = parser.add_subparsers(title='subcommands', dest='command')
    subparsers.required = True

    parser_init = subparsers.add_parser(
        'init',
        help='Initialize the CA root certificate',
        description='Generates the CA key pair and sends an init transaction. '
        'The transaction signer becomes the CA admin, who may revoke any '
        'certificate. Fails if the CA is already initialized.',
        parents=[parent_parser, rest, signing])
    parser_init.add_argument(
        '--key-size', type=int, default=2048, help='CA RSA key size in bits (default: 2048)')

    parser_create = subparsers.add_parser(
        'create',
        help='Request a new certificate',
        description='Generates a key pair and CSR for <name>, has the CA '
        'issue a certificate and saves cert_<serial>.pem and '
        'cert_<serial>.key to the output directory.',
        parents=[parent_parser, rest, signing])
    parser_create.add_argument('name', type=str, help='certificate common name (CN)')
    parser_create.add_argument('--country', default='RU', help='two letter country code (default: RU)')
    parser_create.add_argument('--state', default='Tatarstan', help='state or province (default: Tatarstan)')
    parser_create.add_argument('--locality', default='Innopolis', help='locality (default: Innopolis)')
    parser_create.add_argument('--org', default='SNE', help='organization (default: SNE)')
    parser_create.add_argument('--org-unit', help='organizational unit')
    parser_create.add_argument(
        '--email', help='e-mail address (default: <name> if it contains "@")')
    parser_create.add_argument(
        '--key-size', type=int, default=2048, help='RSA key size in bits (default: 2048)')
    parser_create.add_argument(
        '--out-dir', default='.', help='directory for the certificate and key (default: .)')
    parser_create.add_argument(
        '--encrypt-key', action='store_true',
        help='prompt for a passphrase and encrypt the saved private key')

    parser_revoke = subparsers.add_parser(
        'revoke',
        help='Revoke certificate by serial number',
        description='Revokes a certificate. Only the key that requested the '
        'certificate, or the CA admin, may revoke it.',
        parents=[parent_parser, rest, signing])
    parser_revoke.add_argument('serial', type=_serial, help='certificate serial number')

    parser_get = subparsers.add_parser(
        'get',
        help='Download certificate by serial number',
        description='Reads a certificate from global state and saves it as PEM.',
        parents=[parent_parser, rest])
    parser_get.add_argument('serial', type=_serial, help='certificate serial number')
    parser_get.add_argument(
        '-o', '--output', help='output file (default: cert_<serial>.pem, "-" for stdout)')

    parser_status = subparsers.add_parser(
        'status',
        help='Show certificate status by serial number',
        description='Shows the state (Valid, Revoked or Expired), subject, '
        'validity and owner of a certificate.',
        parents=[parent_parser, rest])
    parser_status.add_argument('serial', type=_serial, help='certificate serial number')

    subparsers.add_parser(
        'list',
        help='List all certificates',
        description='Lists every certificate issued by the CA.',
        parents=[parent_parser, rest])

    parser_ca_cert = subparsers.add_parser(
        'ca-cert',
        help='Download the CA root certificate',
        description='Reads the CA root certificate from global state.',
        parents=[parent_parser, rest])
    parser_ca_cert.add_argument(
        '-o', '--output', default='ca.pem', help='output file (default: ca.pem, "-" for stdout)')

    parser_verify = subparsers.add_parser(
        'verify',
        help='Verify a certificate file',
        description='Checks that a certificate was signed by the CA root, '
        'matches the copy on the ledger, and is neither revoked nor expired. '
        'Exits with status 1 if verification fails.',
        parents=[parent_parser, rest])
    parser_verify.add_argument('certificate', help='PEM certificate file to verify')

    subparsers.add_parser(
        'simple',
        help='Creates a new simple transaction',
        description='Send simple transaction',
        parents=[parent_parser, rest, signing])

    return parser


def do_init(args):
    pkey = create_key_pair(args.key_size)

    # The encrypted key is stored in global state, where the transaction
    # processor decrypts it with the shared CA_KEY_PASSPHRASE.
    data = pkey.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.BestAvailableEncryption(CA_KEY_PASSPHRASE),
    ).decode('utf-8')

    client = _get_client(args, signing=True)
    auth_user, auth_password = _get_auth_info(args)
    _, status = client.init(data, wait=args.wait, auth_user=auth_user, auth_password=auth_password)

    _require_committed(status, 'CA initialization')
    print("CA initialized. Admin public key: {}".format(client.public_key))


def do_create(args):
    email = args.email or (args.name if '@' in args.name else None)
    pkey = create_key_pair(args.key_size)
    csr = create_cert_request(pkey,
                              C=args.country,
                              ST=args.state,
                              L=args.locality,
                              O=args.org,
                              OU=args.org_unit,
                              CN=args.name,
                              emailAddress=email)
    csr = csr.public_bytes(serialization.Encoding.PEM).decode('utf-8')

    key_passphrase = None
    if args.encrypt_key:
        key_passphrase = _prompt_new_passphrase()

    client = _get_client(args, signing=True)
    auth_user, auth_password = _get_auth_info(args)
    serial, status = client.create(csr, wait=args.wait, auth_user=auth_user, auth_password=auth_password)

    _require_committed(status, 'Certificate request', serial)
    record = client.get_record(serial, auth_user=auth_user, auth_password=auth_password)
    if record is None:
        raise CaException("Certificate {} was committed but not found in state".format(serial))

    os.makedirs(args.out_dir, exist_ok=True)
    key_file = os.path.join(args.out_dir, 'cert_{}.key'.format(serial))
    cert_file = os.path.join(args.out_dir, 'cert_{}.pem'.format(serial))
    write_private_file(key_file, serialize_private_key(pkey, key_passphrase))
    write_file(cert_file, record['certificate_string'].encode('utf-8'))

    print("Certificate issued. Serial: {}".format(serial))
    print("  certificate: {}".format(cert_file))
    print("  private key: {}".format(key_file))


def do_revoke(args):
    client = _get_client(args, signing=True)
    auth_user, auth_password = _get_auth_info(args)
    if client.get_record(args.serial, auth_user=auth_user, auth_password=auth_password) is None:
        raise CaException("Certificate {} not found".format(args.serial))

    _, status = client.revoke(args.serial, wait=args.wait, auth_user=auth_user, auth_password=auth_password)

    _require_committed(status, 'Revocation', args.serial)
    print("Certificate {} revoked".format(args.serial))


def do_get(args):
    record = _get_record_or_fail(args)
    pem = record['certificate_string'].encode('utf-8')

    output = args.output or 'cert_{}.pem'.format(args.serial)
    if output == '-':
        sys.stdout.write(pem.decode('utf-8'))
    else:
        write_file(output, pem)
        print("Certificate {} saved to {}".format(args.serial, output))


def do_status(args):
    record = _get_record_or_fail(args)

    print("Serial     : {}".format(record['serial_number']))
    print("Status     : {}".format(record_status(record)))
    print("Subject    : {}".format(record['subject_name']))
    print("Valid till : {}".format(_format_timestamp(record['valid_till_timestamp'])))
    if record.get('revoke_timestamp'):
        print("Revoked at : {}".format(_format_timestamp(record['revoke_timestamp'])))
    print("Owner      : {}".format(record.get('owner') or 'unknown'))


def do_list(args):
    client = _get_client(args)
    auth_user, auth_password = _get_auth_info(args)
    records = client.list_records(auth_user=auth_user, auth_password=auth_password)

    if not records:
        print("No certificates found")
        return

    fmt = "%-20s %-8s %-20s %s"
    print(fmt % ('SERIAL', 'STATUS', 'VALID TILL', 'SUBJECT'))
    for record in records:
        print(fmt % (record['serial_number'],
                     record_status(record),
                     _format_timestamp(record['valid_till_timestamp']),
                     record['subject_name']))


def do_ca_cert(args):
    client = _get_client(args)
    auth_user, auth_password = _get_auth_info(args)
    pem = client.get_ca_certificate(auth_user=auth_user, auth_password=auth_password)
    if pem is None:
        raise CaException("CA is not initialized")

    if args.output == '-':
        sys.stdout.write(pem.decode('utf-8'))
    else:
        write_file(args.output, pem)
        print("CA certificate saved to {}".format(args.output))


def do_verify(args):
    try:
        with open(args.certificate, 'rb') as f:
            cert = x509.load_pem_x509_certificate(f.read())
    except (OSError, ValueError) as err:
        raise CaException("Unable to load certificate {}: {}".format(args.certificate, err))

    client = _get_client(args)
    auth_user, auth_password = _get_auth_info(args)
    ca_pem = client.get_ca_certificate(auth_user=auth_user, auth_password=auth_password)
    if ca_pem is None:
        raise CaException("CA is not initialized")
    record = client.get_record(cert.serial_number, auth_user=auth_user, auth_password=auth_password)

    problems = verify_certificate(cert, x509.load_pem_x509_certificate(ca_pem), record)

    print("Serial  : {}".format(cert.serial_number))
    print("Subject : {}".format(cert.subject.rfc4514_string()))
    if problems:
        for problem in problems:
            print("FAILED  : {}".format(problem))
        sys.exit(1)
    print("OK      : signed by the CA, matches the ledger, not revoked or expired")


def do_simple(args):
    client = _get_client(args, signing=True)
    auth_user, auth_password = _get_auth_info(args)
    status = client.simple('Test data', wait=args.wait, auth_user=auth_user, auth_password=auth_password)
    print("Status: {}".format(status))


def verify_certificate(cert, ca_cert, record, now=None):
    """Check a certificate against the CA root and its on-chain record.

    Returns:
        list of str: reasons the certificate is not trustworthy; empty if valid.
    """
    problems = []
    try:
        cert.verify_directly_issued_by(ca_cert)
    except (ValueError, TypeError, InvalidSignature) as err:
        problems.append("not issued by the CA root ({})".format(str(err) or 'bad signature'))

    if record is None:
        problems.append("serial {} is not on the ledger".format(cert.serial_number))
        return problems

    if record['certificate_string'].encode('utf-8') != cert.public_bytes(serialization.Encoding.PEM):
        problems.append("certificate does not match the copy on the ledger")

    status = record_status(record, now)
    if status != 'Valid':
        problems.append("certificate is {}".format(status.lower()))
    return problems


def record_status(record, now=None):
    """Certificate state, reporting 'Expired' for valid but outdated records."""
    now = now if now is not None else datetime.datetime.now(datetime.timezone.utc).timestamp()
    if record['state'] == 'Valid' and now > record['valid_till_timestamp']:
        return 'Expired'
    return record['state']


def create_key_pair(key_size=2048):
    """
    Create an RSA public/private key pair.
    Arguments: key_size - Number of bits to use in the key
    Returns:   The private key object
    """

    return rsa.generate_private_key(public_exponent=65537, key_size=key_size)


_NAME_OIDS = (
    ('C', NameOID.COUNTRY_NAME),
    ('ST', NameOID.STATE_OR_PROVINCE_NAME),
    ('L', NameOID.LOCALITY_NAME),
    ('O', NameOID.ORGANIZATION_NAME),
    ('OU', NameOID.ORGANIZATIONAL_UNIT_NAME),
    ('CN', NameOID.COMMON_NAME),
    ('emailAddress', NameOID.EMAIL_ADDRESS),
)


def create_cert_request(pkey, **name):
    """
    Create a certificate request.
    Arguments: pkey   - The key to associate with the request
               **name - The name of the subject of the request, possible
                        arguments are:
                          C     - Country name (2 letter code)
                          ST    - State or province name
                          L     - Locality name
                          O     - Organization name
                          OU    - Organizational unit name
                          CN    - Common name
                          emailAddress - E-mail address
                        Attributes that are missing or empty are omitted.
    Returns:   The certificate request object
    """
    try:
        attributes = [x509.NameAttribute(oid, name[key])
                      for key, oid in _NAME_OIDS if name.get(key)]
    except ValueError as err:
        raise CaException("Invalid subject: {}".format(err))

    return x509.CertificateSigningRequestBuilder() \
        .subject_name(x509.Name(attributes)) \
        .sign(pkey, hashes.SHA256())


def serialize_private_key(pkey, passphrase=None):
    if passphrase:
        encryption = serialization.BestAvailableEncryption(passphrase)
    else:
        encryption = serialization.NoEncryption()
    return pkey.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption)


def write_file(file_name, data):
    with open(file_name, "wb") as f:
        f.write(data)


def write_private_file(file_name, data):
    """Write data readable only by the current user, never overwriting a file."""
    try:
        fd = os.open(file_name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except OSError as err:
        raise CaException("Unable to write {}: {}".format(file_name, err))
    with os.fdopen(fd, 'wb') as f:
        f.write(data)


def _require_committed(status, what, serial=None):
    if status != 'COMMITTED':
        suffix = " (serial {})".format(serial) if serial is not None else ""
        raise CaException(
            "{} was not committed{}: batch status is {}. Increase --wait or check "
            "the validator.".format(what, suffix, status))


def _get_record_or_fail(args):
    client = _get_client(args)
    auth_user, auth_password = _get_auth_info(args)
    record = client.get_record(args.serial, auth_user=auth_user, auth_password=auth_password)
    if record is None:
        raise CaException("Certificate {} not found".format(args.serial))
    return record


def _prompt_new_passphrase():
    passphrase = getpass.getpass(prompt="Private key passphrase: ")
    if not passphrase:
        raise CaException("Passphrase must not be empty")
    if passphrase != getpass.getpass(prompt="Repeat passphrase: "):
        raise CaException("Passphrases do not match")
    return passphrase.encode('utf-8')


def _format_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')


def _serial(value):
    if not value.isdigit():
        raise argparse.ArgumentTypeError("serial must be a decimal number: {}".format(value))
    return value


def _get_version():
    try:
        from importlib.metadata import version, PackageNotFoundError
    except ImportError:  # Python < 3.8
        return 'UNKNOWN'
    try:
        return version(DISTRIBUTION_NAME)
    except PackageNotFoundError:
        return 'UNKNOWN'


def _get_client(args, signing=False):
    return CaClient(base_url=_get_url(args), keyfile=_get_keyfile(args) if signing else None)


def _get_url(args):
    return DEFAULT_URL if args.url is None else args.url


def _get_keyfile(args):
    username = getpass.getuser() if args.username is None else args.username
    if args.key_dir is None:
        key_dir = os.path.join(os.path.expanduser("~"), ".sawtooth", "keys")
    else:
        key_dir = os.path.expanduser(args.key_dir)

    return os.path.join(key_dir, '{}.priv'.format(username))


def _get_auth_info(args):
    auth_user = args.auth_user
    auth_password = args.auth_password
    if auth_user is not None and auth_password is None:
        auth_password = getpass.getpass(prompt="Auth Password: ")

    return auth_user, auth_password


COMMANDS = {
    'init': do_init,
    'create': do_create,
    'revoke': do_revoke,
    'get': do_get,
    'status': do_status,
    'list': do_list,
    'ca-cert': do_ca_cert,
    'verify': do_verify,
    'simple': do_simple,
}


def main(prog_name=os.path.basename(sys.argv[0]), args=None):
    if args is None:
        args = sys.argv[1:]
    parser = create_parser(prog_name)
    args = parser.parse_args(args)

    if args.verbose is None:
        verbose_level = 0
    else:
        verbose_level = args.verbose

    setup_loggers(verbose_level=verbose_level)

    command = COMMANDS.get(args.command)
    if command is None:
        raise CaException("invalid command: {}".format(args.command))
    command(args)


def main_wrapper():
    try:
        main()
    except CaException as err:
        print("Error: {}".format(err), file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        pass
    except SystemExit as err:
        raise err
    except BaseException as err:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main_wrapper()
