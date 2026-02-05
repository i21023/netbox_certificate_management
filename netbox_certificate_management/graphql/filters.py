import strawberry_django
from strawberry import auto
from netbox.graphql.filters import NetBoxModelFilter
from .. import models


@strawberry_django.filter(models.Certificate, lookups=True)
class CertificateFilter(NetBoxModelFilter):
    pass
