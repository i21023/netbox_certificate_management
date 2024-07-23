from netbox.api.viewsets import NetBoxModelViewSet
from .. import models
from .serializers import CertificateSerializer

class CertificateViewSet(NetBoxModelViewSet):
    queryset = models.Certificate.objects.prefetch_related(
        'description', 'public_key', 'issuer', 'valid_from', 'valid_to'
        )
    serializer_class = CertificateSerializer