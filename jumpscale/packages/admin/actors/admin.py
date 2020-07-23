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
            j.sals.reservation_chatflow.update_local_reservations()

            return j.data.serializers.json.dumps({"data": {"type": explorer_type, "url": explorers[explorer_type]}})
        else:
            return j.data.serializers.json.dumps(
                {"data": f"{explorer_type} is not a valid explorer type, must be 'testnet' or 'main'"}
            )

    @actor_method
    def list_identities(self) -> str:
        identities = j.core.identity.list_all()
        identity_data = {}
        for identity_name in identities:
            identity = j.core.identity.get(identity_name)
            identity_data[identity_name] = identity.to_dict()
            identity_data[identity_name]["instance_name"] = identity.instance_name
            identity_data[identity_name].pop("__words")
        return j.data.serializers.json.dumps({"data": identity_data})

    @actor_method
    def get_identity(self, identity_instance_name: str) -> str:
        identity_names = j.core.identity.list_all()
        if identity_instance_name in identity_names:
            identity = j.core.identity.get(identity_instance_name)

            return j.data.serializers.json.dumps(
                {
                    "data": {
                        "instance_name": identity.instance_name,
                        "name": identity.tname,
                        "email": identity.email,
                        "tid": identity.tid,
                        "explorer_url": identity.explorer_url,
                    }
                }
            )
        else:
            return j.data.serializers.json.dumps({"data": f"{identity_instance_name} doesn't exist"})

    @actor_method
    def set_identity(self, identity_instance_name: str) -> str:
        identity_names = j.core.identity.list_all()
        if identity_instance_name in identity_names:
            j.core.identity.set_default(identity_instance_name)

            # update our solutions
            j.sals.reservation_chatflow.update_local_reservations()

            return j.data.serializers.json.dumps({"data": {"instance_name": identity_instance_name}})
        else:
            return j.data.serializers.json.dumps({"data": f"{identity_instance_name} doesn't exist"})

    @actor_method
    def add_identity(self, identity_instance_name: str, tname: str, email: str, words: str, explorer_type: str) -> str:
        explorer_url = f"https://{explorers[explorer_type]}/explorer"
        if identity_instance_name in j.core.identity.list_all():
            return j.data.serializers.json.dumps({"data": "Identity with the same instance name already exists"})
        new_identity = j.core.identity.new(
            name=identity_instance_name, tname=tname, email=email, words=words, explorer_url=explorer_url
        )
        new_identity.register()
        new_identity.save()
        return j.data.serializers.json.dumps({"data": "New identity successfully created and registered"})

    @actor_method
    def delete_identity(self, identity_instance_name: str) -> str:
        identity_names = j.core.identity.list_all()
        if identity_instance_name in identity_names:
            identity = j.core.identity.get(identity_instance_name)
            if identity.instance_name == j.core.identity.me.instance_name:
                return j.data.serializers.json.dumps({"data": "Cannot delete current default identity"})

            j.core.identity.delete(identity_instance_name)
            return j.data.serializers.json.dumps({"data": f"{identity_instance_name} deleted successfully"})
        else:
            return j.data.serializers.json.dumps({"data": f"{identity_instance_name} doesn't exist"})


Actor = Admin
