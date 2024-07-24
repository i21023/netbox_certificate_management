from netbox.forms import NetBoxModelForm
from django.forms import DateTimeField, DateTimeInput, Form, FileField
from utilities.forms.widgets import DateTimePicker
from utilities.forms.fields import CommentField
from .models import Certificate

class CertificateForm(NetBoxModelForm):
    
    #valid_to=DateTimeField(widget=DateTimePicker())
    #valid_from=DateTimeField(widget=DateTimePicker())
    comments=CommentField()

    class Meta:
        model = Certificate
        fields = []


class CertificateUploadForm(Form):
    file = FileField(label='Certificate file')