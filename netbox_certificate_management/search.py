from netbox.search import SearchIndex
from .models import Certificate

class CertificateIndex(SearchIndex):
    model = Certificate
    fields = (
        ('subject', 100),
        ('issuer_name', 500),
        ('comments', 5000)
    )