from netbox.filtersets import NetBoxModelFilterSet
from .models import Certificate
from django_filters import filters
from django.db.models import Q

class CertificateFilterSet(NetBoxModelFilterSet):

    valid_days_left=filters.NumberFilter(method='filter_valid_days_left')
    sans=filters.CharFilter(method='filter_sans')

    class Meta:
        model = Certificate
        fields = (
            'id',
            'subject',
            'issuer',
            'devices',
            'virtual_machines',
            'valid_days_left',
            'sans'
        )

    def search(self, queryset, name, value):
        return queryset.filter(subject__icontains=value)

    def filter_valid_days_left(self, queryset, name, value):
        return queryset.filter(valid_days_left__lte=value)

    def filter_sans(self, queryset, name, value):
        matching_certificates = []

        for certificate in queryset:
            # Access the sans property directly
            if any(value.lower() in san_value.lower() for san in certificate.sans for san_value in san.values()):
                matching_certificates.append(certificate.id)

        # Return the filtered queryset
        return queryset.filter(id__in=matching_certificates)
