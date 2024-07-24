import django_tables2 as tables

from netbox.tables import NetBoxTable, ChoiceFieldColumn
from .models import Certificate


class CertificateTable(NetBoxTable):

    valid_days_left=tables.Column()

    class Meta:
        model = Certificate
        #template_name = 'django_tables2/bootstrap.html'
        fields = ('pk', 'serial_number', 'subject', 'issuer', 'not_valid_before', 'not_valid_after', 'valid_days_left', 'devices', 'actions')
        default_columns = ('subject', 'issuer', 'valid_days_left')
    