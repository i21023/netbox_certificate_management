from netbox.plugins import PluginMenuItem, PluginMenuButton
from django.utils.translation import gettext_lazy as _

menu_items = (
    PluginMenuItem(
        link='plugins:netbox_certificate_management:certificate_list',
        link_text=_('certificates')
    ),
)