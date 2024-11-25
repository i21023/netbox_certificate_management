from django.conf import settings

plugin_settings = settings.PLUGINS_CONFIG["netbox_certificate_management"]

# default parameter values if not provided in configuration.py
WARNING_THRESHOLD = plugin_settings.get("WARNING_THRESHOLD", 30)
CRITICAL_THRESHOLD = plugin_settings.get("CRITICAL_THRESHOLD", 14)
