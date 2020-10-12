def export_module_as():
    from jumpscale.core.base import StoredFactory
    from .notificationservice import NotificationService

    return StoredFactory(NotificationService)
