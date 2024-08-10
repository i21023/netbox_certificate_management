from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12, pkcs7
import base64

def parse_certificate(cert: bytes, password: str = None) -> (dict, str):
    """
    Takes in a certificate in any format (PEM, DER, PKCS#12, PKCS#7) and returns a tuple with the parsed
    certificate data and the certificate in PEM format.
    """
    if password is not None:
        pem_cert_bytes = convert_pkcs12_to_pem(cert, password)
    else:
        pem_cert_bytes = detect_certificate_format_and_convert_to_pem(cert)

    pem_cert = x509.load_pem_x509_certificate(pem_cert_bytes, default_backend())

    if(pem_cert.version != x509.Version.v3):
        raise ValueError('Only x509 v3 certificates are supported')
    
    data = {
        'subject': pem_cert.subject.rfc4514_string(),
        'serial_number': pem_cert.serial_number,
        'subject_public_key': pem_cert.public_key().public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo).decode('utf-8'),
        'subject_public_key_algorithm': pem_cert.public_key().__class__.__name__,
        'not_valid_before': pem_cert.not_valid_before_utc.isoformat(),
        'not_valid_after': pem_cert.not_valid_after_utc.isoformat(),
        'issuer_name': pem_cert.issuer.rfc4514_string(),
        'signature_algorithm': pem_cert.signature_algorithm_oid._name,
    }
    return data, base64.b64encode(pem_cert_bytes).decode('utf-8')

def detect_certificate_format_and_convert_to_pem(cert_data: bytes) -> bytes:
    """
    Takes in a certificate in any format (PEM, DER, PKCS#12, PKCS#7) in binary and returns the certificate in PEM format.
    Raises a ValueError if the certificate format is not supported.
    """

    # Try to load as PEM
    try:
        return x509.load_pem_x509_certificate(cert_data, default_backend()).public_bytes(encoding=serialization.Encoding.PEM)
    except ValueError:
        print("Not PEM")
        pass

    # Try to load as DER
    try:
        cert = x509.load_der_x509_certificate(cert_data, default_backend())
        return cert.public_bytes(encoding=serialization.Encoding.PEM)
    except ValueError:
        print("Not DER")
        pass  # Not DER format

    # Try to load as PKCS#12
    try:
        _, cert, _ = pkcs12.load_key_and_certificates(data = cert_data, backend= default_backend(), password=None)
        if cert is not None:
            return cert.public_bytes(encoding=serialization.Encoding.PEM)
    except ValueError:
        print("Not PKCS#12")
        pass  # Not PKCS#12 format

    # Try to load as PKCS#7
    try:
        certificates = pkcs7.load_der_pkcs7_certificates(cert_data)
        if certificates:
            return certificates[0].public_bytes(encoding=serialization.Encoding.PEM) # Return the first certificate found
    except ValueError:
        print("Not PKCS#7")
        pass  # Not PKCS#7 format

    raise ValueError("Unsupported certificate format")


def convert_pem_to_der(pem_cert: bytes) -> bytes:
    """
    Takes in a certificate in PEM format and returns the certificate in DER format.
    """
    return x509.load_pem_x509_certificate(pem_cert, default_backend()).public_bytes(encoding=serialization.Encoding.DER)

def convert_pkcs12_to_pem(cert_data: bytes, password: str) -> bytes:
    """
    Takes in a PKCS#12 certificate and key in binary and returns the certificate in PEM format.
    """
    try:
        print(password)
        _, cert, _ = pkcs12.load_key_and_certificates(data = cert_data, backend=default_backend(), password=password.encode('utf-8'))
        return cert.public_bytes(encoding=serialization.Encoding.PEM)
    except ValueError:
        raise ValueError('Either the password is wrong or the file is not in PKCS#12 format')








