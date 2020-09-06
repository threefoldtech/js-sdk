import os
from urllib.parse import urlparse
from jumpscale.loader import j
from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.packages.backup.actors.marketplace import Backup


BACKUP_ACTOR = Backup()

# TODO: edit naming
explorer_url_to_name = {"explorer.grid.tf": "main", "explorer.testnet.grid.tf": "testnet"}
explorer_url_from_name = {"main": "explorer.grid.tf", "testnet": "explorer.testnet.grid.tf"}


class Identity(BaseActor):
    @actor_method
    def get_identity(self, identity_instance_name: str = None) -> str:
        """
        @param: identity_instance_name: which identity to get its info,
                if not passed will return default identity info
        """

        identity_names = j.core.identity.list_all()
        if not identity_names:
            return j.data.serializers.json.dumps({"data": f"You have to configure an identity"})

        if not identity_instance_name:
            identity = j.core.identity.me
        else:
            if identity_instance_name not in identity_names:
                return j.data.serializers.json.dumps({"data": f"{identity_instance_name} doesn't exist"})
            identity = j.core.identity.get(identity_instance_name)

        network = explorer_url_to_name.get(urlparse(j.core.identity.me.explorer.url).netloc, "Unknown")
        return j.data.serializers.json.dumps(
            {
                "data": {
                    "instance_name": identity.instance_name,
                    "name": identity.tname,
                    "email": identity.email,
                    "tid": identity.tid,
                    "network": network.capitalize(),
                    "explorer_url": identity.explorer_url,
                }
            }
        )

    @actor_method
    def set_identity(self, label: str, tname: str, email: str, words: str, backup_password: str = None):
        j.core.identity.get(label, tname=tname, email=email, words=words)
        j.core.identity.set_default(label)
        j.core.config.set("threebot_connect", True)
        if backup_password:
            BACKUP_ACTOR.init(backup_password, False)
            BACKUP_ACTOR.restore()

    @actor_method
    def set_default_identity(self, identity_instance_name: str) -> str:
        identity_names = j.core.identity.list_all()
        if identity_instance_name in identity_names:
            j.core.identity.set_default(identity_instance_name)

            return j.data.serializers.json.dumps({"data": {"instance_name": identity_instance_name}})
        else:
            return j.data.serializers.json.dumps({"data": f"{identity_instance_name} doesn't exist"})

    @actor_method
    def add_identity(self, identity_instance_name: str, tname: str, email: str, words: str, explorer_type: str) -> str:
        explorer_url = f"https://{explorer_url_from_name[explorer_type]}/api/v1"
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
    def get_explorer_url(self) -> str:
        return j.data.serializers.json.dumps({"url": j.core.identity.me.explorer.url})


Actor = Identity
