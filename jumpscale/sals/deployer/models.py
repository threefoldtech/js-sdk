from datetime import datetime

from jumpscale.core.base import Base, fields
from enum import Enum
from jumpscale.sals.reservation_chatflow.models import SolutionType


class MarketPlaceSolution(Base):
    id = fields.Integer()
    name = fields.String(default="")
    tid = fields.Integer()
    solution_type = fields.Enum(SolutionType)
    rid = fields.Integer()
    form_info = fields.Typed(dict)
    explorer = fields.String(default="")
