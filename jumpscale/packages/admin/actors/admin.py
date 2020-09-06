from jumpscale.loader import j
from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.core.exceptions import JSException


explorers = {"main": "explorer.grid.tf", "testnet": "explorer.testnet.grid.tf"}


class Admin(BaseActor):
    @actor_method
    def list_admins(self) -> str:
        admins = list(set(j.core.identity.me.admins))
        return j.data.serializers.json.dumps({"data": admins})

    @actor_method
    def add_admin(self, name: str):
        if name in j.core.identity.me.admins:
            raise j.exceptions.Value(f"Admin {name} already exists")
        j.core.identity.me.admins.append(name)
        j.core.identity.me.save()

    @actor_method
    def delete_admin(self, name: str):
        if name not in j.core.identity.me.admins:
            raise j.exceptions.Value(f"Admin {name} does not exist")
        j.core.identity.me.admins.remove(name)
        j.core.identity.me.save()

    @actor_method
    def list_explorers(self) -> str:
        return j.data.serializers.json.dumps({"data": explorers})

    @actor_method
    def get_developer_options(self) -> str:
        test_cert = j.core.config.get("TEST_CERT")
        over_provision = j.core.config.get("OVER_PROVISIONING")
        return j.data.serializers.json.dumps({"data": {"test_cert": test_cert, "over_provision": over_provision}})

    @actor_method
    def set_developer_options(self, test_cert: bool, over_provision: bool) -> str:
        j.core.config.set("TEST_CERT", test_cert)
        j.core.config.set("OVER_PROVISIONING", over_provision)
        return j.data.serializers.json.dumps({"data": {"test_cert": test_cert, "over_provision": over_provision}})


Actor = Admin
