from enum import Enum
from uuid import uuid4

from jumpscale.core.base import Base, StoredFactory, fields
from jumpscale.loader import j


class UserEntry(Base):
    explorer_url = fields.String()
    tname = fields.String()
    has_agreed = fields.Boolean(default=False)


class UserRole(Enum):
    ADMIN = "ADMIN"
    USER = "USER"


class APIKey(Base):
    key = fields.String(default=lambda: uuid4().hex)
    role = fields.Enum(UserRole)
    created_at = fields.Float(default=lambda: j.data.time.utcnow().timestamp)

    def to_dict(self):
        d = super().to_dict()
        d["name"] = self.instance_name
        return d


APIKeyFactory = StoredFactory(APIKey)
APIKeyFactory.always_reload = True
