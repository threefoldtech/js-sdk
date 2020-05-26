def export_module_as():
    from jumpscale.core.base import StoredFactory

    from .mail import MailClient

    return StoredFactory(MailClient)
