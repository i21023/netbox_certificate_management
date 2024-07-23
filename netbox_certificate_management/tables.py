import django_tables2 as tables

from netbox.tables import NetBoxTable, ChoiceFieldColumn
from .models import Certificate


class CertificateTable(NetBoxTable):

    class Meta:
        model = Certificate
        template_name = 'django_tables2/bootstrap.html'
        fields = ('pk', 'name', 'description', 'issuer', 'valid_from', 'valid_to', 'actions')
        default_columns = ('name', 'description', 'issuer', 'valid_from', 'valid_to')
    