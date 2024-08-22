from unicodedata import decimal

from django.db import models
from mptt.managers import TreeManager
from netbox.models import NetBoxModel
from django.urls import reverse
import django.contrib.postgres.fields as pg_fields
from django.db.models import JSONField, F, ForeignKey, UniqueConstraint
from utilities.choices import ChoiceSet
from cryptography.x509 import NameOID, Name, NameAttribute
from cryptography.x509.oid import ObjectIdentifier
from django.core.exceptions import ValidationError
from mptt.models import TreeForeignKey, MPTTModel
from django.utils.translation import gettext_lazy as _

class Certificate(NetBoxModel, MPTTModel):
    """
    Represents a x509 v3 certificate
    """
    serial_number=models.DecimalField(decimal_places=0, max_digits=100)
    signature_algorithm=models.CharField()
    issuer_name=models.CharField()
    issuer=TreeForeignKey('self', related_name='certificates', on_delete=models.SET_NULL, null=True, blank=True) #this is used to sort the list by hierarchy and subjects for the table view
    not_valid_before=models.DateTimeField()
    not_valid_after=models.DateTimeField()
    subject=models.CharField()
    subject_public_key_algorithm=models.CharField()
    subject_public_key=models.CharField()
    extensions=JSONField(blank=True, null=True, default=dict)
    devices=models.ManyToManyField('dcim.Device', related_name='certificates', blank=True)
    virtual_machines=models.ManyToManyField('virtualization.VirtualMachine', related_name='certificates', blank=True)
    comments=models.TextField(blank=True)
    file=models.BinaryField()
    is_root=models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('plugins:netbox_certificate_management:certificate_detail', args=[self.pk])

    def __str__(self):
        return self.subject

    @property
    def depth(self):
        return self.get_level()

    @property
    def sans(self):
        return self.extensions.get('san', [])

    @property
    def key_usage(self):
        return self.extensions.get('key_usage', {})

    @property
    def basic_constraints(self):
        return self.extensions.get('basic_constraints', {})

    @property
    def extended_key_usage(self):
        return self.extensions.get('extended_key_usage', [])

    @property
    def crl_distribution_points(self):
        return self.extensions.get('crl_distribution_points', [])

    class Meta:
        verbose_name_plural=_('certificates')
        verbose_name=_('certificate')
        constraints=[
            UniqueConstraint(fields=['serial_number', 'issuer_name'], name='unique_serial_issuer')
        ]

    class MPTTMeta:
        order_insertion_by=['subject']
        parent_attr='issuer'
