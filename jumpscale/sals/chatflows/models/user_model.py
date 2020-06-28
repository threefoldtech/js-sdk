from jumpscale.core.base import Base, fields


class User(Base):
    user_code = fields.String(default="")
    poll_name = fields.String(default="")
    transaction_hash = fields.String(default="")
    vote_data = fields.Typed(dict, default={})
    has_voted = fields.Boolean(default=False)
