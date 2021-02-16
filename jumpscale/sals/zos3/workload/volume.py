from jumpscale.core.base import Base, fields

from . import Data, DeviceType, Result


class Volume(Data):
    size = fields.Integer(min=1)
    type = fields.Enum(DeviceType)
