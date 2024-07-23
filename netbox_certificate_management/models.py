from django.db import models 
from netbox.models import NetBoxModel
from django.urls import reverse

class Certificate(NetBoxModel):
    name=models.CharField(max_length=100)
    description=models.TextField(blank=True)
    public_key=models.TextField()
    issuer=models.CharField(max_length=100)
    valid_from=models.DateTimeField()
    valid_to=models.DateTimeField()
    devices=models.ManyToManyField('dcim.Device', blank=True)

    class Meta:
        ordering = ('valid_to',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plugins:netbox_certificate_management:certificate', args=[self.pk])