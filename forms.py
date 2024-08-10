from netbox.forms import NetBoxModelForm

from .models import Certificate

class CertificateForm(NetBoxModelForm):
    class Meta:
        model=Certificate
        fields='serial_number, signature_algorithm, issuer, '