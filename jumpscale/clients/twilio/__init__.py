def export_module_as():
    from jumpscale.core.base import StoredFactory
    from .twilio import TwilioSMSClient

    StoredFactory(TwilioSMSClient)
