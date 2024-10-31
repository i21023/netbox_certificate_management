from netbox.filtersets import NetBoxModelFilterSet
from .models import Certificate
from django_filters import filters
from django.db.models import Q
from datetime import datetime, timezone, timedelta, date

class CertificateFilterSet(NetBoxModelFilterSet):

    valid_days_left=filters.NumberFilter(method='filter_valid_days_left')
    valid_days_left__lt=filters.NumberFilter(method="filter_valid_days_left_lt")
    valid_days_left__gt=filters.NumberFilter(method='filter_valid_days_left_gt')
    valid_days_left__lte=filters.NumberFilter(method='filter_valid_days_left_lte')
    valid_days_left__gte=filters.NumberFilter(method='filter_valid_days_left_gte')
    sans=filters.CharFilter(method='filter_sans')

    class Meta:
        model = Certificate
        fields = (
            'id',
            'subject',
            'issuer',
            'devices',
            'virtual_machines'
        )

    def search(self, queryset, name, value):
        return queryset.filter(subject__icontains=value)

    def filter_sans(self, queryset, name, value):
        matching_certificates = []

        for certificate in queryset:
            # Access the sans property directly
            if any(value.lower() in san_value.lower() for san in certificate.sans for san_value in san.values()):
                matching_certificates.append(certificate.id)

        # Return the filtered queryset
        return queryset.filter(id__in=matching_certificates)
    
    def filter_valid_days_left(self, queryset, name, value):
        return queryset.filter(not_valid_after=datetime.now(timezone.utc) + timedelta(days=int(value)))

    def filter_valid_days_left_lt(self, queryset, name, value):
        print(datetime.now(timezone.utc) + timedelta(days=int(value)))
        return queryset.filter(not_valid_after__lt=datetime.now(timezone.utc) + timedelta(days=int(value)))

    def filter_valid_days_left_gt(self, queryset, name, value):
        print(datetime.now(timezone.utc) + timedelta(days=int(value)))
        return queryset.filter(not_valid_after__gt=datetime.now(timezone.utc) + timedelta(days=int(value)))

    def filter_valid_days_left_lte(self, queryset, name, value):
        return queryset.filter(not_valid_after__lte=datetime.now(timezone.utc) + timedelta(days=int(value)))

    def filter_valid_days_left_gte(self, queryset, name, value):
        print(datetime.now(timezone.utc) + timedelta(days=int(value)))
        return queryset.filter(not_valid_after__gte=datetime.now(timezone.utc) + timedelta(days=int(value)))