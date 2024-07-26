from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

def parse_certificate(certificate):
    cert = x509.load_pem_x509_certificate(data=certificate, backend=default_backend())
    return {
        'version': cert.version,
        'subject': cert.subject,
        'serial_number': cert.serial_number,
        'public_key': cert.public_key().public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo),
        'not_valid_before': cert.not_valid_before_utc,
        'not_valid_after': cert.not_valid_after_utc,
        'issuer': cert.issuer,
    }
