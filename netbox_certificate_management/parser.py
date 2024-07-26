from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

def parse_certificate(certificate):
    cert = x509.load_pem_x509_certificate(data=certificate, backend=default_backend())
    
    # Convert version to match the choices in VersionChoice
    version_map = {
        x509.Version.v1: 'v1',
        x509.Version.v3: 'v3'
    }
    
    return {
        'version': version_map.get(cert.version, 'v3'),  # Default to 'v3' if version is not found
        'subject': cert.subject.rfc4514_string(),
        'serial_number': cert.serial_number,
        'public_key': cert.public_key().public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo).decode('utf-8'),
        'not_valid_before': cert.not_valid_before_utc.isoformat(),
        'not_valid_after': cert.not_valid_after_utc.isoformat(),
        'issuer_name': cert.issuer.rfc4514_string(),
    }
