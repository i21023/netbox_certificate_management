from django.db import models 
from netbox.models import NetBoxModel
from django.urls import reverse
from utilities.choices import ChoiceSet

class VersionChoice(ChoiceSet):
    key='Certificate.versions'

    CHOICES=[
        ('v1', 'v1'),
        ('v2', 'v2'),
        ('v3', 'v3'),
    ]

class Certificate(NetBoxModel):
    serial_number=models.CharField()
    signature_algorithm=models.CharField(null=True)
    subject=models.CharField()
    public_key=models.TextField()
    issuer_name=models.CharField()
    issuer=models.ForeignKey('self', blank=True, null=True, default=None, on_delete=models.SET_NULL)
    not_valid_before=models.DateTimeField()
    not_valid_after=models.DateTimeField()
    devices=models.ManyToManyField('dcim.Device', blank=True)
    comments=models.TextField(blank=True)
    version=models.CharField(
        max_length=5,
        choices=VersionChoice
    )

    class Meta:
        ordering = ('not_valid_after',)

    def __str__(self):
        return self.subject

    def get_absolute_url(self):
        return reverse('plugins:netbox_certificate_management:certificate', args=[self.pk])
    
