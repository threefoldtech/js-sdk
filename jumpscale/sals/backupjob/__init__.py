def export_module_as():
    from .backupjob import BackupJob
    from jumpscale.core.base import StoredFactory

    return StoredFactory(BackupJob)
