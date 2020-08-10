from jumpscale.core.base import Base, fields


class PoolConfig(Base):
    pool_id = fields.Integer()
    name = fields.String()
    hidden = fields.Boolean(default=False)
