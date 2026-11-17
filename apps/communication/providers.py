import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class BaseProvider:
    def send(self, recipient, body, subject=""):
        raise NotImplementedError("Subclasses must implement send method")


class LogOnlySMSProvider(BaseProvider):
    def send(self, recipient, body, subject=""):
        phone = getattr(recipient, 'phone', '').strip()
        if not phone:
            return False, "Missing phone number"
        logger.info(f"[SMS DEV PROVIDER] Sent to {phone}: {body[:100]}...")
        return True, None


class LogOnlyWhatsAppProvider(BaseProvider):
    def send(self, recipient, body, subject=""):
        phone = getattr(recipient, 'phone', '').strip()
        if not phone:
            return False, "Missing phone number"
        logger.info(f"[WHATSAPP DEV PROVIDER] Sent to {phone}: {body[:100]}...")
        return True, None


def get_sms_provider():
    # Pluggable via settings.SMS_PROVIDER_CLASS if defined in future
    provider_path = getattr(settings, 'SMS_PROVIDER_CLASS', None)
    if provider_path:
        from django.utils.module_loading import import_string
        return import_string(provider_path)()
    return LogOnlySMSProvider()


def get_whatsapp_provider():
    # Pluggable via settings.WHATSAPP_PROVIDER_CLASS if defined in future
    provider_path = getattr(settings, 'WHATSAPP_PROVIDER_CLASS', None)
    if provider_path:
        from django.utils.module_loading import import_string
        return import_string(provider_path)()
    return LogOnlyWhatsAppProvider()
