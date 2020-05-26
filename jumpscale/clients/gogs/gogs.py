from jumpscale.clients.base import Base, Client
from jumpscale.core.base import fields


class User(Base):
    username = fields.String(required=True)
    password = fields.Secret(required=True)


class Gogs(Client):
    access_token = fields.Secret(required=True)
    user = fields.Object(User)
    admins = fields.List(fields.String(required=True), required=True)
