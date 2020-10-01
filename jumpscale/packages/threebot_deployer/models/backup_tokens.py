from jumpscale.core.base import Base, fields
from jumpscale.loader import j


class BackupTokens(Base):
    tname = fields.String()
    token = fields.String()
