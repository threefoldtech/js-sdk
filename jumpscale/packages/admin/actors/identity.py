import os
from urllib.parse import urlparse
from jumpscale.loader import j
from jumpscale.servers.gedis.baseactor import BaseActor, actor_method


class Identity(BaseActor):
    @actor_method
    def get_identity(self) -> str:
        data = None
        if j.core.identity.list_all():
            data = {
                "id": j.core.identity.me.tid,
                "name": j.core.identity.me.tname,
                "email": j.core.identity.me.email,
            }
        return j.data.serializers.json.dumps(data)

    @actor_method
    def set_identity(self, label: str, tname: str, email: str, words: str):
        j.core.identity.get(label, tname=tname, email=email, words=words)
        j.core.identity.set_default(label)
        j.core.config.set("threebot_connect", True)

    @actor_method
    def list_identities(self) -> str:
        identities = {}
        for label in j.core.identity.list_all():
            identity = j.core.identity.get(label)
            identities[label] = {"name": identity.tname, "email": identity.email}
        return j.data.serializers.json.dumps(identities)


Actor = Identity
