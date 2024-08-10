import django_tables2 as tables
from django_tables2.utils import Accessor
from django.utils.translation import gettext_lazy as _

from netbox.tables import NetBoxTable, ColoredLabelColumn, ColorColumn, TemplateColumn
from .models import Certificate
from .columns import ColorStatusColumn

CERTIFICATE_LINK = """
{% if record.pk %}
  <a href="{{ record.get_absolute_url }}" id="certificate_{{ record.pk }}">{{ record.subject }}</a>
{% endif %}
"""

CERTIFICATE_LINK_WITH_DEPTH = """
{% load helpers %}
{% if record.depth %}
    <div class="record-depth">
        {% for i in record.depth|as_range %}
            <span>•</span>
        {% endfor %}
    </div>
{% endif %}
""" + CERTIFICATE_LINK

class CertificateTable(NetBoxTable):
    subject=TemplateColumn(
        template_code=CERTIFICATE_LINK_WITH_DEPTH,
        verbose_name=_('Subject')
    )
    valid_days_left = ColorStatusColumn()
    issuer = tables.Column(
        linkify=True
    )
    # subject = tables.Column(
    #     linkify=True
    # )
    depth=tables.Column(
        accessor=Accessor('level'),
        verbose_name=_('Depth')
    )

    class Meta(NetBoxTable.Meta):
        model = Certificate
        fields = (
            'pk', 'serial_number', 'issuer', 'subject', 'not_valid_before', 'not_valid_after', 'valid_days_left', 'depth', 'devices', 'virtual_machines', 'comments', 'actions'
        )
        default_columns = (
            'subject', 'issuer', 'valid_days_left', 'default_action'
        )