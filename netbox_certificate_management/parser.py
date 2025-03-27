from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12 
import base64
import socket
import ssl

GENERAL_NAME_MAPPING = {
    x509.DNSName: 'DNS',
    x509.RFC822Name: 'Email',
    x509.IPAddress: 'IP',
    x509.UniformResourceIdentifier: 'URI',
    x509.DirectoryName: 'DirName',
    x509.RegisteredID: 'RegisteredID',
    x509.OtherName: 'OtherName'
}

def parse_san_extension(extensions) -> list[dict] | None:
    """
    Parses the Subject Alternative Name (SAN) extension from the certificate extensions.

    Args:
        extensions (x509.Extensions): The extensions of the certificate.

    Returns:
        list[dict] | None: A list of dictionaries containing the SANs or None if the extension is not found.
    """
    try:
        san_extension = extensions.get_extension_for_class(x509.SubjectAlternativeName)
        sans = []
        for name in san_extension.value:
            if isinstance(name, x509.IPAddress):
                sans.append({GENERAL_NAME_MAPPING.get(name.__class__): name.value.exploded})
            else:
                sans.append({GENERAL_NAME_MAPPING.get(name.__class__): name.value})
        return sans
    except x509.ExtensionNotFound:
        return None

def parse_basic_constraints_extension(extensions) -> dict | None:
    """
    Parses the Basic Constraints extension from the certificate extensions.

    Args:
        extensions (x509.Extensions): The extensions of the certificate.

    Returns:
        dict | None: A dictionary containing the basic constraints or None if the extension is not found.
    """
    try:
        basic_constraints_extension = extensions.get_extension_for_class(x509.BasicConstraints)
        return {
            'ca': basic_constraints_extension.value.ca,
            'path_length': basic_constraints_extension.value.path_length
        }
    except x509.ExtensionNotFound:
        return None

def parse_key_usage_extension(extensions) -> dict | None:
    """
    Parses the Key Usage extension from the certificate extensions.

    Args:
        extensions (x509.Extensions): The extensions of the certificate.

    Returns:
        dict | None: A dictionary containing the key usage or None if the extension is not found.
    """
    try:
        key_usage_extension = extensions.get_extension_for_class(x509.KeyUsage)
        return {
            'digital_signature': key_usage_extension.value.digital_signature,
            'content_commitment': key_usage_extension.value.content_commitment,
            'key_encipherment': key_usage_extension.value.key_encipherment,
            'data_encipherment': key_usage_extension.value.data_encipherment,
            'key_agreement': key_usage_extension.value.key_agreement,
            'key_cert_sign': key_usage_extension.value.key_cert_sign,
            'crl_sign': key_usage_extension.value.crl_sign
        }
    except x509.ExtensionNotFound:
        return None

def parse_extended_key_usage_extension(extensions) -> list | None:
    """
    Parses the Extended Key Usage extension from the certificate extensions.

    Args:
        extensions (x509.Extensions): The extensions of the certificate.

    Returns:
        list | None: A list of extended key usages or None if the extension is not found.
    """
    try:
        extended_key_usage_extension = extensions.get_extension_for_class(x509.ExtendedKeyUsage)
        extended_keys = []
        for key in extended_key_usage_extension.value:
            extended_keys.append(key._name)
        return extended_keys
    except x509.ExtensionNotFound:
        return None

def parse_crl_distribution_points_extension(extensions) -> list[dict] | None:
    """
    Parses the CRL Distribution Points extension from the certificate extensions.

    Args:
        extensions (x509.Extensions): The extensions of the certificate.

    Returns:
        list[dict] | None: A list of dictionaries containing the CRL distribution points or None if the extension is not found.
    """
    try:
        crl_dist_points_extension = extensions.get_extension_for_class(x509.CRLDistributionPoints)
        crl_dist_points = []
        for dist_point in crl_dist_points_extension.value:
            for dist_point_name in dist_point.full_name:
                crl_dist_points.append({
                    GENERAL_NAME_MAPPING.get(dist_point_name.__class__): dist_point_name.value
                })
        return crl_dist_points
    except x509.ExtensionNotFound:
        return None

def parse_certificate(cert: bytes, password: str = None) -> tuple[dict, str]:
    """
    Takes in a certificate in any format (PEM, DER, PKCS#12, PKCS#7) and returns a tuple with the parsed
    certificate data and the certificate in PEM format.

    Args:
        cert (bytes): The certificate data in binary format.
        password (str, optional): The password for PKCS#12 certificates. Defaults to None.

    Returns:
        tuple: A tuple containing the parsed certificate data as a dictionary and the certificate in PEM format as a string.
    """
    if password is not None:
        pem_cert_bytes = convert_pkcs12_to_pem(cert, password)
    else:
        pem_cert_bytes = detect_certificate_format_and_convert_to_pem(cert)

    pem_cert = x509.load_pem_x509_certificate(pem_cert_bytes, default_backend())

    if(pem_cert.version != x509.Version.v3):
        raise ValueError('Only x509 v3 certificates are supported')

    # Parse extensions
    extensions = {}
    san_extension = parse_san_extension(pem_cert.extensions)
    if san_extension: extensions['san'] = san_extension
    basic_contraints_extension = parse_basic_constraints_extension(pem_cert.extensions)
    if basic_contraints_extension: extensions['basic_constraints'] = basic_contraints_extension
    key_usage_extension = parse_key_usage_extension(pem_cert.extensions)
    if key_usage_extension: extensions['key_usage'] = key_usage_extension
    extended_key_usage_extension = parse_extended_key_usage_extension(pem_cert.extensions)
    if extended_key_usage_extension: extensions['extended_key_usage'] = extended_key_usage_extension
    crl_distribution_points_extension = parse_crl_distribution_points_extension(pem_cert.extensions)
    if crl_distribution_points_extension: extensions['crl_distribution_points'] = crl_distribution_points_extension

    data = {
        'subject': pem_cert.subject.rfc4514_string(),
        'serial_number': pem_cert.serial_number,
        'subject_public_key': pem_cert.public_key().public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo).decode('utf-8'),
        'subject_public_key_algorithm': pem_cert.public_key().__class__.__name__,
        'not_valid_before': pem_cert.not_valid_before_utc.isoformat(),
        'not_valid_after': pem_cert.not_valid_after_utc.isoformat(),
        'issuer_name': pem_cert.issuer.rfc4514_string(),
        'signature_algorithm': pem_cert.signature_algorithm_oid._name,
        'extensions': extensions
    }
    return data, base64.b64encode(pem_cert_bytes).decode('utf-8')

def detect_certificate_format_and_convert_to_pem(cert_data: bytes) -> bytes:
    """
    Takes in a certificate in any format (PEM, DER, PKCS#12, PKCS#7) in binary and returns the certificate in PEM format.
    Raises a ValueError if the certificate format is not supported.

    Args:
        cert_data (bytes): The certificate data in binary format.

    Returns:
        bytes: The certificate in PEM format.
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

    raise ValueError("Unsupported certificate format")


def convert_pem_to_der(pem_cert: bytes) -> bytes:
    """
    Takes in a certificate in PEM format and returns the certificate in DER format.

    Args:
        pem_cert (bytes): The certificate in PEM format.

    Returns:
        bytes: The certificate in DER format.
    """
    return x509.load_pem_x509_certificate(pem_cert, default_backend()).public_bytes(encoding=serialization.Encoding.DER)

def convert_pkcs12_to_pem(cert_data: bytes, password: str) -> bytes:
    """
    Takes in a PKCS#12 certificate and key in binary and returns the certificate in PEM format.

    Args:
        cert_data (bytes): The PKCS#12 certificate data in binary format.
        password (str): The password for the PKCS#12 certificate.

    Returns:
        bytes: The certificate in PEM format.
    """
    try:
        print(password)
        _, cert, _ = pkcs12.load_key_and_certificates(data = cert_data, backend=default_backend(), password=password.encode('utf-8'))
        return cert.public_bytes(encoding=serialization.Encoding.PEM)
    except ValueError:
        raise ValueError('Either the password is wrong or the file is not in PKCS#12 format')


def fetch_https_certificate(url: str) -> bytes:
    """
    Fetches the SSL certificate from the given URL.

    Args:
        url (str): The URL to fetch the certificate from.

    Returns:
        bytes: The certificate in binary format.

    Raises:
        ValueError: If there is an error fetching the certificate.
    """
    try:
        url=url.split('://')[1]
        context = ssl.create_default_context()
        with socket.create_connection((url, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=url) as ssock:
                cert = ssock.getpeercert(binary_form=True)
                return cert
    except Exception as e:
        raise ValueError(f'Error fetching certificate: {e}')
