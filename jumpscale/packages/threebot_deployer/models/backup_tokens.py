from jumpscale.core.base import Base, fields


class BackupTokens(Base):
    tname = fields.String()
    token = fields.String()
