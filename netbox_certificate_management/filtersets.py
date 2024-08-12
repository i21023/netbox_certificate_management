from netbox.filtersets import NetBoxModelFilterSet
from .models import Certificate
from django_filters import filters

class CertificateFilterSet(NetBoxModelFilterSet):

    valid_days_left=filters.NumberFilter(method='filter_valid_days_left')

    class Meta:
        model = Certificate
        fields = (
            'id',
            'subject',
            'issuer',
            'devices',
            'virtual_machines',
            'valid_days_left',
        )

    def search(self, queryset, name, value):
        return queryset.filter(subject__icontains=value)

    def filter_valid_days_left(self, queryset, name, value):
        return queryset.filter(valid_days_left__lte=value)