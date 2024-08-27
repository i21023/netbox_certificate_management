from django.db import models
from django.db.models import Case, When, Value, IntegerField


class CertificateQuerySet(models.QuerySet):
    def ordered_by_hierarchy(self):
        return self.order_by(
            Case(
                When(issuer__isnull=True, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            ),
            'issuer',
            'subject'
        )

class CertificateManager(models.Manager):
    def get_queryset(self):
        return CertificateQuerySet(self.model, using=self._db)

    def ordered_by_hierarchy(self):
        return self.get_queryset().ordered_by_hierarchy()