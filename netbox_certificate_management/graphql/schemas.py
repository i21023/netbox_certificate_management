import strawberry
import strawberry_django
from typing import List
from .types import CertificateType


@strawberry.type(name="Query")
class CertificateQuery:
    certificate_list: List[CertificateType] = strawberry_django.field()
    certificate: CertificateType = strawberry_django.field()
