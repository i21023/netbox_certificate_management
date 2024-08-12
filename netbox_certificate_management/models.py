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
#
# class OIDField(models.CharField):
#
#         description="A field to store Object Identifier (OID)"
#
#         def __init__(self, *args, **kwargs):
#             super().__init__(*args, **kwargs)
#
#         def is_valid_oid(self, oid_str):
#             try:
#                 # Parse the OID string
#                 ObjectIdentifier(oid_str)
#                 return True
#             except Exception:
#                 return False
#
#         def validate(self, value, model_instance):
#             super().validate(value, model_instance)
#             if not self.is_valid_oid(value):
#                 raise ValidationError(f"Invalid OID: {value}")
#
# class DNField(models.CharField):
#
#     description="A field to store Distinguished Name (DN)"
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#     def is_valid_dn(self, dn_str):
#         try:
#             # Parse the DN string into a Name object
#             attributes = []
#             for part in dn_str.split(','):
#                 key, value = part.split('=')
#                 oid = getattr(NameOID, key.upper())
#                 attributes.append(NameAttribute(oid, value))
#
#             # Create a Name object, which will validate the DN
#             Name(attributes)
#             return True
#         except Exception:
#             return False
#
#     def validate(self, value, model_instance):
#         super().validate(value, model_instance)
#         if not self.is_valid_dn(value):
#             raise ValidationError(f"Invalid DN: {value}")

# class VersionChoice(ChoiceSet):
#     key='Certificate.versions'

#     CHOICES=[
#         (0, 'v1'),
#         (2, 'v3'),
#     ]

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

    class Meta:
        verbose_name_plural=_('certificates')
        verbose_name=_('certificate')
        constraints=[
            UniqueConstraint(fields=['serial_number', 'issuer_name'], name='unique_serial_issuer')
        ]

    class MPTTMeta:
        order_insertion_by=['subject']
        parent_attr='issuer'
