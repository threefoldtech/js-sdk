from jumpscale.core.base import Base, fields
from jumpscale.loader import j


class UserEntry(Base):
    tname = fields.String()
    has_agreed = fields.Boolean(default=False)