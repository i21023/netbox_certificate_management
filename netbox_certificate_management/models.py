from django.db import models 
from netbox.models import NetBoxModel
from django.urls import reverse

class Certificate(NetBoxModel):
    serial_number=models.BinaryField(max_length=20)
    signature_algorithm=models.CharField()
    subject=models.CharField()
    public_key=models.TextField()
    issuer_name=models.CharField()
    issuer=models.ForeignKey('self', blank=True, null=True, default=None, on_delete=models.SET_NULL)
    not_valid_before=models.DateTimeField()
    not_valid_after=models.DateTimeField()
    devices=models.ManyToManyField('dcim.Device', blank=True)
    comments=models.TextField(blank=True)

    class Meta:
        ordering = ('not_valid_after',)

    def __str__(self):
        return self.subject

    def get_absolute_url(self):
        return reverse('plugins:netbox_certificate_management:certificate', args=[self.pk])