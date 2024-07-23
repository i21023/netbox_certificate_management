from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer
from ..models import Certificate

class CertificateSerializer(NetBoxModelSerializer):

    url=serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_certificate_management-api:certificate-detail'
    )

    class Meta:
        model = Certificate
        fields = (
            'id', 'url', 'display', 'name', 'description', 'public_key', 'issuer', 'valid_from', 'valid_to', 'device', 'custom_fields', 'created',
        )