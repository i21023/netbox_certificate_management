from netbox.api.viewsets import NetBoxModelViewSet

from .. import models
from .serializers import CertificateSerializer
from ..utils import return_days_valid
from .. import filtersets

class CertificateViewSet(NetBoxModelViewSet):
    queryset = models.Certificate.objects.prefetch_related(
        'devices',
        'virtual_machines',
        'tags'
    ).annotate(
        valid_days_left=return_days_valid(),
    )
    serializer_class = CertificateSerializer
    filterset_class=filtersets.CertificateFilterSet