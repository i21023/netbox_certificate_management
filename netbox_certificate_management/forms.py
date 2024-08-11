from graphene import Dynamic
from netbox.forms import NetBoxModelForm
from .models import Certificate
from utilities.forms.fields import CommentField, DynamicModelMultipleChoiceField
from dcim.models import Device
from virtualization.models import VirtualMachine
from django import forms
from utilities.forms.widgets import DateTimePicker

class CertificateForm(NetBoxModelForm):

    #not_valid_before=forms.DateTimeField(widget=DateTimePicker())
    #not_valid_after=forms.DateTimeField(widget=DateTimePicker())
    devices = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False
    )
    virtual_machines = DynamicModelMultipleChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False
    )
    subject_public_key = forms.CharField(widget=forms.Textarea)
    comments=CommentField()

    class Meta:
        model = Certificate
        fields = ('devices',
                  'virtual_machines',
                  'comments',
                  'subject',
                  'issuer',
                  'issuer_name',
                  'serial_number',
                  'not_valid_before',
                  'not_valid_after',
                  'signature_algorithm',
                  'subject_public_key_algorithm',
                  'subject_public_key',
                  'extensions',
                  'tags'
                  )

class URLForm(forms.Form):
    url = forms.URLField(label='URL', required=True)