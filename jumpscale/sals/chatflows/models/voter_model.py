from jumpscale.core.base import Base, fields


class User(Base):
    user_code = fields.String(default="")
    poll_name = fields.String(default="")
    wallet_address = fields.String(default="")
    transaction_hash = fields.String(default="")
    vote_data = fields.Typed(dict, default={})
    vote_data_weighted = fields.Typed(dict, default={})
    has_voted = fields.Boolean(default=False)
