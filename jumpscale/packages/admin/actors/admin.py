from jumpscale.loader import j
from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.core.exceptions import JSException

explorers = {"main": "explorer.grid.tf", "testnet": "explorer.testnet.grid.tf"}


class Admin(BaseActor):
    @actor_method
    def list_admins(self) -> str:
        return j.data.serializers.json.dumps({"data": j.core.identity.me.admins})

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
    def get_current_user(self) -> str:
        return j.data.serializers.json.dumps(
            {
                "data": {
                    "name": j.core.identity.me.tname,
                    "email": j.core.identity.me.email,
                    "tid": j.core.identity.me.tid,
                }
            }
        )

    @actor_method
    def list_explorers(self) -> str:
        return j.data.serializers.json.dumps({"data": explorers})

    @actor_method
    def get_explorer(self) -> str:
        current_url = j.core.identity.me.explorer_url.strip().lower().split("/")[2]
        if current_url == explorers["testnet"]:
            explorer_type = "testnet"
        elif current_url == explorers["main"]:
            explorer_type = "main"
        else:
            return j.data.serializers.json.dumps({"data": {"type": "custom", "url": current_url}})
        return j.data.serializers.json.dumps({"data": {"type": explorer_type, "url": explorers[explorer_type]}})

    @actor_method
    def set_explorer(self, explorer_type: str) -> str:
        if explorer_type in explorers:
            me = j.core.identity.me
            url = f"https://{explorers[explorer_type]}/explorer"
            client = j.clients.explorer.get(name=explorer_type, url=url)
            # check if we can switch with existing identity
            try:
                user = client.users.get(name=me.tname, email=me.email)
            except j.exceptions.NotFound:
                raise j.exceptions.NotFound(f"Your identity does not exist on {explorer_type}")

            if user.pubkey != j.core.identity.me.nacl.get_verify_key_hex():
                raise j.exceptions.Value(f"Your identity does not match on {explorer_type}")

            j.clients.explorer.default_addr_set(url=url)

            # update our solutions
            j.sals.reservation_chatflow.get_solutions_explorer()

            return j.data.serializers.json.dumps({"data": {"type": explorer_type, "url": explorers[explorer_type]}})
        else:
            return j.data.serializers.json.dumps(
                {"data": f"{explorer_type} is not a valid explorer type, must be 'testnet' or 'main'"}
            )


Actor = Admin
