from netbox.search import SearchIndex, register_search
from .models import Certificate


@register_search
class CertificateIndex(SearchIndex):
    model = Certificate
    fields = (
        ('subject', 100),
        ('issuer_name', 500),
        ('comments', 5000)
    )