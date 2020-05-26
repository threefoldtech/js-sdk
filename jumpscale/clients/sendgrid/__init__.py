def export_module_as():
    from jumpscale.core.base import StoredFactory
    from .sendgrid import SendGridClient

    return StoredFactory(SendGridClient)
