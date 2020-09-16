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
                        "words": identity.words,
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

            return j.data.serializers.json.dumps({"data": {"instance_name": identity_instance_name}})
        else:
            return j.data.serializers.json.dumps({"data": f"{identity_instance_name} doesn't exist"})

    @actor_method
    def add_identity(self, identity_instance_name: str, tname: str, email: str, words: str, explorer_type: str) -> str:
        explorer_url = f"https://{explorers[explorer_type]}/api/v1"
        if identity_instance_name in j.core.identity.list_all():
            return j.data.serializers.json.dumps({"data": "Identity with the same instance name already exists"})
        try:
            new_identity = j.core.identity.new(
                name=identity_instance_name, tname=tname, email=email, words=words, explorer_url=explorer_url
            )
            new_identity.register()
            new_identity.save()
        except Exception as e:
            j.core.identity.delete(identity_instance_name)
            raise j.exceptions.Value(str(e))
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

    @actor_method
    def get_developer_options(self) -> str:
        test_cert = j.core.config.set_default("TEST_CERT", False)
        over_provision = j.core.config.set_default("OVER_PROVISIONING", False)
        return j.data.serializers.json.dumps({"data": {"test_cert": test_cert, "over_provision": over_provision}})

    @actor_method
    def set_developer_options(self, test_cert: bool, over_provision: bool) -> str:
        j.core.config.set("TEST_CERT", test_cert)
        j.core.config.set("OVER_PROVISIONING", over_provision)
        return j.data.serializers.json.dumps({"data": {"test_cert": test_cert, "over_provision": over_provision}})

    @actor_method
    def clear_blocked_nodes(self) -> str:
        j.sals.reservation_chatflow.reservation_chatflow.clear_blocked_nodes() 
        return j.data.serializers.json.dumps({"data": "blocked nodes got cleared successfully."})

Actor = Admin
