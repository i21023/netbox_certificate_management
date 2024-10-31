import strawberry
import strawberry_django
from typing import Annotated, List, Union, Optional
from decimal import Decimal
from .filters import *
from .. import models
from netbox.graphql.types import OrganizationalObjectType
from datetime import datetime, timezone

@strawberry_django.type(
    models.Certificate,
    fields='subject devices issuer not_valid_before not_valid_after issuer_name virtual_machines serial_number',
    filters=CertificateFilter
)
class CertificateType(OrganizationalObjectType):
    subject: str
    issuer: Annotated['CertificateType', strawberry.lazy('netbox_certificate_management.graphql.types')] | None
    issuer_name: str
    devices: List[Annotated['DeviceType', strawberry.lazy('dcim.graphql.types')]]
    virtual_machines: List[Annotated['VirtualMachineType', strawberry.lazy('virtualization.graphql.types')]]
    not_valid_before: datetime
    not_valid_after: datetime
    serial_number: Decimal
    valid_days_left: int

    @strawberry.field
    def valid_days_left(self) -> int:
        return (self.not_valid_after - datetime.now(timezone.utc)).days
