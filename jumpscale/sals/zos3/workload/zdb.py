from enum import Enum
from jumpscale.core.base import fields

from . import Data, DeviceType


class Mode(Enum):
    USER = "user"
    SEQ = "seq"


class ZDB(Data):
    size = fields.Integer(min=1)
    mode = fields.Enum(Mode)
    password_encrypted = fields.String()
    disk_type = fields.Enum(DeviceType)
    public = fields.Boolean()
