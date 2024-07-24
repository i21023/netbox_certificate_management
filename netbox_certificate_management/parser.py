from cryptography import x509

def parse_certificate(certificate):
    cert = x509.load_pem_x509_certificate(certificate.encode())
    return {
        'subject': cert.subject.rfc4514_string(),
        'issuer': cert.issuer.rfc4514_string(),
        'not_valid_before': cert.not_valid_before,
        'not_valid_after': cert.not_valid_after,
        'serial_number': cert.serial_number,
        'public_key': cert.public_key().public_bytes().decode(),
    }
