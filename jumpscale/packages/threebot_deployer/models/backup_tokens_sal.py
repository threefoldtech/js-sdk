from jumpscale.core.base import StoredFactory
from jumpscale.packages.threebot_deployer.models.backup_tokens import BackupTokens

BACKUP_MODEL_FACTORY = StoredFactory(BackupTokens)
BACKUP_MODEL_FACTORY.always_reload = True
