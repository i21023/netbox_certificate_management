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
            'pk', 'url', 'subject', 'public_key', 'issuer_name', 'issuer', 'not_valid_before', 'not_valid_after', 'devices', 'comments'
        )