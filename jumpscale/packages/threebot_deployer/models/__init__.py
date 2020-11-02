from jumpscale.core.base import StoredFactory
from .backup_tokens import BackupTokens
from .user_solutions import UserThreebot

BACKUP_MODEL_FACTORY = StoredFactory(BackupTokens)
BACKUP_MODEL_FACTORY.always_reload = True

USER_THREEBOT_FACTORY = StoredFactory(UserThreebot)
USER_THREEBOT_FACTORY.always_reload = True
