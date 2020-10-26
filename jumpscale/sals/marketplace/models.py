from jumpscale.core.base import Base, fields


class UserPool(Base):
    pool_id = fields.Integer()
    owner = fields.String()
    explorer_url = fields.String()
