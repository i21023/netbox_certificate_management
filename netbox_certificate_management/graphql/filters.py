import strawberry_django
from strawberry import auto
from netbox.graphql.filter_mixins import autotype_decorator, BaseFilterMixin
from .. import models, filtersets


@strawberry_django.filter(models.Certificate, lookups=True)
@autotype_decorator(filtersets.CertificateFilterSet)
class CertificateFilter(BaseFilterMixin):
    pass