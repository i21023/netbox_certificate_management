from netbox.api.viewsets import NetBoxModelViewSet

from .. import models
from .serializers import CertificateSerializer
from ..utils import return_days_valid
from .. import filtersets
from ..config import *

from django.db.models import Case, When, Value, CharField


class CertificateViewSet(NetBoxModelViewSet):
    queryset = models.Certificate.objects.prefetch_related(
        "devices", "virtual_machines", "tags"
    ).annotate(
        valid_days_left=return_days_valid(),
        status=Case(
            When(valid_days_left__lte=CRITICAL_THRESHOLD, then=Value("critical")),
            When(valid_days_left__lte=WARNING_THRESHOLD, then=Value("warning")),
            default=Value("ok"),
            output_field=CharField(),
        ),
    )
    serializer_class = CertificateSerializer
    filterset_class = filtersets.CertificateFilterSet
