import django_tables2 as tables
from django_tables2.utils import Accessor
from django.utils.translation import gettext_lazy as _

from netbox.tables import NetBoxTable, ColoredLabelColumn, ColorColumn, TemplateColumn, columns
from .models import Certificate

VALID_DAYS_LEFT="""
{% if record.valid_days_left < 0 %}
    <span class="badge" style="background-color: red; color: white">{{record.valid_days_left}}</span>
{% elif record.valid_days_left < 30 %}
    <span class="badge" style="background-color: orange; color: white">{{record.valid_days_left}}</span>
{% else %}
    <span class="badge" style="background-color: green; color: white">{{record.valid_days_left}}</span>
{% endif %}
"""

DEVICES = """
{% for dev in value.all %}
    <a href="{% url 'dcim:device' pk=dev.pk %}">{{ dev }}</a>{% if not forloop.last %}, {% endif %}
{% endfor %}
"""

CERTIFICATE_LINK = """
{% if record.pk %}
    <a href="{{ record.get_absolute_url }}" id="certificate_{{ record.pk }}">{{ record.subject }} </a>
    {% if not record.is_root and record.depth == 0 %} 
       <span style="color: #eb5726;" class="mdi mdi-alert-outline" data-bs-toggle="tooltip" title='{{ certificate_tooltip }}'></span>
    {% endif %}
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

ISSUER_COLUMN_TEMPLATE = """
{% if record.issuer %}
    <a href="{{ record.issuer.get_absolute_url }}">{{ record.issuer }}</a>
{% elif record.issuer_name and not record.is_root %}
    {{ record.issuer_name }}
{% else %}
    <span>—</span>
{% endif %}
"""

class CertificateTable(NetBoxTable):
    subject=TemplateColumn(
        template_code=CERTIFICATE_LINK_WITH_DEPTH,
        extra_context={'certificate_tooltip': _('root_cert_warn')},
        verbose_name=_('subject')
    )
    valid_days_left = TemplateColumn(
        template_code=VALID_DAYS_LEFT,
        verbose_name=_('days_left')
    )
    issuer = TemplateColumn(
        template_code=ISSUER_COLUMN_TEMPLATE,
        verbose_name=_('issuer')
    )
    depth=tables.Column(
        accessor=Accessor('level'),
        verbose_name=_('Depth')
    )
    devices = columns.TemplateColumn(
        template_code=DEVICES,
        orderable=False,
        verbose_name=_('Devices')
    )
    virtual_machines = columns.TemplateColumn(
        template_code=DEVICES,
        orderable=False,
        verbose_name=_('Virtual Machines')
    )
    not_valid_before = tables.DateTimeColumn(
        verbose_name=_('not_valid_before')
    )
    not_valid_after = tables.DateTimeColumn(
        verbose_name=_('not_valid_after')
    )
    sans = tables.Column(
        verbose_name=_('sans')
    )

    class Meta(NetBoxTable.Meta):
        model = Certificate
        fields = (
            'pk', 'serial_number', 'issuer', 'subject', 'not_valid_before', 'not_valid_after', 'valid_days_left', 'sans', 'depth', 'devices', 'virtual_machines', 'comments', 'actions'
        )
        default_columns = (
            'subject', 'issuer', 'valid_days_left', 'default_action'
        )

    def render_sans(self, value):
        # Extract SAN values
        san_values = []
        for entry in value:
            for san_value in entry.values():
                san_values.append(san_value)

        # Return as comma-separated string
        return ', '.join(san_values)