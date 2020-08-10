from jumpscale.core.base import Base, fields


class PoolConfig(Base):
    pool_id = fields.Integer()
    name = fields.String(default="")
    hidden = fields.Boolean(default=False)
