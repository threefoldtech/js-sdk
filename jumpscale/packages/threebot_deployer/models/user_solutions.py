from jumpscale.core.base import Base, fields


class UserThreebot(Base):
    # instance name is the solution uuid
    explorer_url = fields.String()
    name = fields.String()
    owner_tname = fields.String()  # owner's tname in 3bot connect after cleaning
    compute_pool_id = fields.Integer()
    gateway_pool_id = fields.Integer()
    threebot_wid = fields.Integer()
    trc_wid = fields.Integer()
    subdomain_wid = fields.Integer()
    proxy_wid = fields.Integer()  # can't be retrieved in most cases
    farm_name = fields.String()
