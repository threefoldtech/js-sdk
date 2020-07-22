from jumpscale.core.base import Base, fields


class User(Base):
    user_code = fields.String(default="")
    poll_name = fields.String(default="")
    wallets_addresses = fields.List(fields.String())
    transaction_hashes = fields.List(fields.String())
    tokens = fields.Float(default=0.0)
    vote_data = fields.Typed(dict, default={})
    extra_data = fields.Typed(dict, default={})
    vote_data_weighted = fields.Typed(dict, default={})
    has_voted = fields.Boolean(default=False)
    manifesto_version = fields.String(default="2.0.0")
