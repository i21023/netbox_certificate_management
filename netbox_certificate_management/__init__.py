from netbox.plugins import PluginConfig

class NetBoxCertificateManagementConfig(PluginConfig):
    name = 'netbox_certificate_management'
    verbose_name = ' NetBox Access Lists'
    description = 'Manage simple ACLs in NetBox'
    version = '0.1'
    base_url = 'certificates'


config = NetBoxCertificateManagementConfig