"""
Certificate generation module.

NOTE: this module runs inside the transaction processor container
(Python 3.5), so it must not use f-strings or other newer syntax.
"""

import calendar

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization


_NAME_OIDS = (
    ('C', NameOID.COUNTRY_NAME),
    ('ST', NameOID.STATE_OR_PROVINCE_NAME),
    ('L', NameOID.LOCALITY_NAME),
    ('O', NameOID.ORGANIZATION_NAME),
    ('OU', NameOID.ORGANIZATIONAL_UNIT_NAME),
    ('CN', NameOID.COMMON_NAME),
    ('emailAddress', NameOID.EMAIL_ADDRESS),
)


def create_key_pair(key_size=2048):
    """
    Create an RSA public/private key pair.
    Arguments: key_size - Number of bits to use in the key
    Returns:   The private key object
    """

    pkey = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )
    return pkey


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

    attributes = [x509.NameAttribute(oid, name[key])
                  for key, oid in _NAME_OIDS if name.get(key)]

    csr = x509.CertificateSigningRequestBuilder() \
        .subject_name(x509.Name(attributes)) \
        .sign(pkey, hashes.SHA256(), default_backend())

    return csr


def create_certificate(request, issuer_cert, issuer_key, not_before, not_after, serial, is_ca=False):
    """
    Generate a certificate given a certificate request.
    Arguments: request     - Certificate request to use
               issuer_cert - The certificate (or CSR, when self-signing) of the issuer
               issuer_key  - The private key of the issuer
               not_before  - Datetime when the certificate starts being valid
               not_after   - Datetime when the certificate stops being valid
               serial      - Serial number for the certificate. It must be
                             deterministic, because every validator re-executes
                             this transaction and must produce identical state.
               is_ca       - Whether the certificate may sign other certificates
    Returns:   The signed certificate object
    """
    builder = x509.CertificateBuilder() \
        .subject_name(request.subject) \
        .issuer_name(issuer_cert.subject) \
        .public_key(request.public_key()) \
        .serial_number(serial) \
        .not_valid_before(not_before) \
        .not_valid_after(not_after) \
        .add_extension(x509.BasicConstraints(ca=is_ca, path_length=0 if is_ca else None), critical=True) \
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(request.public_key()), critical=False) \
        .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(issuer_key.public_key()),
                       critical=False)

    builder = builder.add_extension(x509.KeyUsage(digital_signature=not is_ca,
                                                  content_commitment=False,
                                                  key_encipherment=not is_ca,
                                                  data_encipherment=False,
                                                  key_agreement=False,
                                                  key_cert_sign=is_ca,
                                                  crl_sign=is_ca,
                                                  encipher_only=False,
                                                  decipher_only=False), critical=True)

    return builder.sign(issuer_key, hashes.SHA256(), default_backend())


def utc_timestamp(dt):
    """Convert a naive-UTC or aware datetime to a POSIX timestamp.

    Unlike datetime.timestamp(), this does not depend on the host time zone,
    which matters because every validator must compute the same state.
    """
    return calendar.timegm(dt.utctimetuple())


def not_valid_after(cert):
    try:
        return cert.not_valid_after_utc
    except AttributeError:  # cryptography < 42
        return cert.not_valid_after


def subject_to_string(subject):
    try:
        return subject.rfc4514_string()
    except AttributeError:  # cryptography < 2.5
        return str(subject)


def serialize_certificate(cert):
    return cert.public_bytes(serialization.Encoding.PEM)


def deserialize_certificate(data):
    return x509.load_pem_x509_certificate(data, default_backend())


def deserialize_pkey(data, passphrase):
    return serialization.load_pem_private_key(data=data, password=passphrase, backend=default_backend())
