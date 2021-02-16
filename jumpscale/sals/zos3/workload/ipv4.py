from jumpscale.core.base import Base, fields

from . import Data, Result


class PublicIP(Data):
    ip = fields.IPAddress(required=True)


class PublicIPResult(Result):
    pass
