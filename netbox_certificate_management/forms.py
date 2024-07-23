from netbox.forms import NetBoxModelForm
from .models import Certificate

class CertificateForm(NetBoxModelForm):
    class Meta:
        model = Certificate
        fields = ['name', 'description', 'public_key', 'issuer', 'valid_from', 'valid_to']