from netbox.forms import NetBoxModelForm
from django.forms import DateTimeField, DateTimeInput, Form, FileField
from utilities.forms.widgets import DateTimePicker
from utilities.forms.fields import CommentField, DynamicModelMultipleChoiceField, DynamicModelChoiceField
from .models import Certificate
from dcim.models import Device

class CertificateForm(NetBoxModelForm):
    
    not_valid_before=DateTimeField(widget=DateTimePicker())
    not_valid_after=DateTimeField(widget=DateTimePicker())
    comments=CommentField()

    devices=DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False
    )

    class Meta:
        model = Certificate
        fields = ['version', 'serial_number', 'subject', 'public_key', 'issuer_name', 'issuer', 'not_valid_before', 'not_valid_after', 'devices', 'comments']


class CertificateUploadForm(Form):
    file = FileField(label='Certificate file')