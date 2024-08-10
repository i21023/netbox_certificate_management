from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer
from dcim.api.serializers import DeviceSerializer
from virtualization.api.serializers import VirtualMachineSerializer
from ..models import Certificate

class CertificateSerializer(NetBoxModelSerializer):
    url=serializers.HyperlinkedIdentityField(view_name='plugins-api:netbox_certificate_management-api:certificate-detail')
    devices=DeviceSerializer(many=True, read_only=True)
    virtual_machines=VirtualMachineSerializer(many=True, read_only=True)

    class Meta:
        model = Certificate
        fields = ('id', 'url', 'subject', 'issuer_name', 'comments', 'not_valid_after', 'not_valid_before', 'devices', 'virtual_machines', 'created', 'last_updated')