from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer
from dcim.api.serializers import DeviceSerializer
from virtualization.api.serializers import VirtualMachineSerializer
from ..models import Certificate


class CertificateSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_certificate_management-api:certificate-detail"
    )
    devices = DeviceSerializer(many=True, read_only=True)
    virtual_machines = VirtualMachineSerializer(many=True, read_only=True)
    valid_days_left = serializers.IntegerField(read_only=True)
    status = serializers.CharField(read_only=True)
    file = serializers.CharField(read_only=True)

    class Meta:
        model = Certificate
        fields = (
            "id",
            "url",
            "subject",
            "issuer_name",
            "comments",
            "not_valid_after",
            "not_valid_before",
            "valid_days_left",
            "status",
            "devices",
            "virtual_machines",
            "file",
            "created",
            "last_updated",
        )
