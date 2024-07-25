from netbox.plugins import PluginConfig

class NetBoxCertificateManagementConfig(PluginConfig):
    name = 'netbox_certificate_management'
    verbose_name = ' NetBox Certificate Management'
    description = 'Manage certificates in NetBox'
    version = '0.1'
    base_url = 'certificates'


config = NetBoxCertificateManagementConfig