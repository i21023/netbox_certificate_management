from netbox.search import SearchIndex, register_search
from .models import Certificate


@register_search
class CertificateIndex(SearchIndex):
    """
    This class is used to define the fields that are searchable in the global search bar and the priority of the search results
    """
    model = Certificate
    fields = (
        ('subject', 100),
        ('issuer_name', 500),
        ('comments', 5000)
    )