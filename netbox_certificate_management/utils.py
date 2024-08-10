from datetime import datetime, timezone
from django.db.models.functions import ExtractDay
from django.db.models import F
from . import models

def return_days_valid():
    return ExtractDay(F('not_valid_after') - datetime.now(timezone.utc))


def get_hierarchical_order(queryset):
    # Convert the queryset to a list and create a dictionary with parent_id as the key
    def append_children(cert):
        children = list(models.Certificate.objects.filter(issuer=cert).order_by('subject'))
        print(children)
        for child in children:
            sorted_certificates.append(child)
            append_children(child)

    certificates = list(queryset)
    root_certs = [cert for cert in certificates if cert.issuer is None]
    root_certs.sort(key=lambda x: x.subject)

    sorted_certificates = []

    for root_cert in root_certs:
        sorted_certificates.append(root_cert)
        append_children(root_cert)

    cert_ids = [cert.id for cert in sorted_certificates]
    print(cert_ids)
    certificates = models.Certificate.objects.filter(pk__in=cert_ids)

    return certificates


