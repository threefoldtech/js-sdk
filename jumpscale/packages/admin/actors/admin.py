from jumpscale.loader import j
from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.core.exceptions import JSException
from requests import HTTPError
import json

explorers = {"main": "explorer.grid.tf", "testnet": "explorer.testnet.grid.tf", "devnet": "explorer.devnet.grid.tf"}


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
            try:
                identity = j.core.identity.get(identity_name)
                if identity.tid < 0:
                    continue
                identity_dict = identity.to_dict()
                identity_dict["instance_name"] = identity.instance_name
                identity_dict.pop("__words")
            except Exception as e:
                j.logger.exception("error", exception=e)
                # TODO: include traceback
                j.tools.alerthandler.alert_raise(
                    app_name="admin",
                    category="internal_errors",
                    message=f"failed to get identity {identity_name} info due to error {str(e)}",
                    alert_type="exception",
                )
                continue
            identity_data[identity_name] = identity_dict
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
    def get_current_identity_name(self) -> str:
        return j.data.serializers.json.dumps({"data": j.core.identity.me.instance_name})

    @actor_method
    def set_identity(self, identity_instance_name: str) -> str:
        identity_names = j.core.identity.list_all()
        if identity_instance_name in identity_names:
            j.core.identity.set_default(identity_instance_name)

            return j.data.serializers.json.dumps({"data": {"instance_name": identity_instance_name}})
        else:
            return j.data.serializers.json.dumps({"data": f"{identity_instance_name} doesn't exist"})

    def generate_mnemonic(self) -> str:
        words = j.data.encryption.generate_mnemonic()
        return j.data.serializers.json.dumps({"data": words})

    @actor_method
    def check_tname_exists(self, tname, explorer_type) -> str:
        explorer_clients = {
            "main": j.clients.explorer.get("user_checker_mainnet", f"https://{explorers['main']}/api/v1"),
            "testnet": j.clients.explorer.get("user_checker_testnet", f"https://{explorers['testnet']}/api/v1"),
            "devnet": j.clients.explorer.get("user_checker_testnet", f"https://{explorers['testnet']}/api/v1"),
        }
        explorer_client = explorer_clients[explorer_type]
        try:
            explorer_client.users.get(name=tname)
            return j.data.serializers.json.dumps({"data": True})
        except j.exceptions.NotFound:
            return j.data.serializers.json.dumps({"data": False})

    @actor_method
    def check_identity_instance_name(self, name) -> str:
        if name in j.core.identity.list_all():
            return j.data.serializers.json.dumps({"data": True})
        return j.data.serializers.json.dumps({"data": False})

    @actor_method
    def add_identity(self, display_name: str, tname: str, email: str, words: str, explorer_type: str) -> str:
        if not display_name.isidentifier() or not display_name.islower():
            raise j.exceptions.Value(
                "The display name must be a lowercase valid python identitifier (English letters, underscores, and numbers not starting with a number)."
            )
        identity_instance_name = display_name
        explorer_url = f"https://{explorers[explorer_type]}/api/v1"
        if identity_instance_name in j.core.identity.list_all():
            raise j.exceptions.Value("Identity with the same name already exists")
        try:
            new_identity = j.core.identity.new(
                name=identity_instance_name, tname=tname, email=email, words=words, explorer_url=explorer_url
            )
            new_identity.register()
            new_identity.save()
        except HTTPError as e:
            j.core.identity.delete(identity_instance_name)
            try:
                raise j.exceptions.Value(j.data.serializers.json.loads(e.response.content)["error"])
            except (KeyError, json.decoder.JSONDecodeError):
                # Return the original error message in case the explorer returned unexpected
                # result, or it failed for some reason other than Bad Request error
                raise j.exceptions.Value(str(e))
        except Exception as e:
            # register sometimes throws exceptions other than HTTP like Input
            j.core.identity.delete(identity_instance_name)
            raise j.exceptions.Value(str(e))
        return j.data.serializers.json.dumps({"data": "New identity successfully created and registered"})

    @actor_method
    def get_config(self) -> str:
        config_obj = j.core.config.get_config()
        return j.data.serializers.json.dumps({"data": config_obj})

    @actor_method
    def get_sdk_version(self) -> str:
        import importlib_metadata as metadata

        packages = ["js-ng", "js-sdk"]
        data = {}
        for package in packages:
            data[package] = metadata.version(package)
        return j.data.serializers.json.dumps({"data": data})

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
    def list_sshkeys(self) -> str:
        sshkeys = j.core.config.get("SSH_KEYS", {})
        return j.data.serializers.json.dumps({"data": sshkeys})

    @actor_method
    def add_sshkey(self, key_id, sshkey) -> str:
        sshkeys = j.core.config.get("SSH_KEYS", {})
        if key_id not in sshkeys:
            sshkeys[key_id] = sshkey
            j.core.config.set("SSH_KEYS", sshkeys)
        return j.data.serializers.json.dumps({"data": sshkeys})

    @actor_method
    def delete_sshkey(self, key_id) -> str:
        sshkeys = j.core.config.get("SSH_KEYS", {})
        if key_id in sshkeys:
            sshkeys.pop(key_id)
            j.core.config.set("SSH_KEYS", sshkeys)
        return j.data.serializers.json.dumps({"data": sshkeys})

    @actor_method
    def get_developer_options(self) -> str:
        test_cert = j.core.config.set_default("TEST_CERT", False)
        over_provision = j.core.config.set_default("OVER_PROVISIONING", False)
        explorer_logs = j.core.config.set_default("EXPLORER_LOGS", False)
        escalation_emails = j.core.config.set_default("ESCALATION_EMAILS_ENABLED", False)
        auto_extend_pools = j.core.config.set_default("AUTO_EXTEND_POOLS_ENABLED", True)
        sort_nodes_by_sru = j.core.config.set_default("SORT_NODES_BY_SRU", False)
        return j.data.serializers.json.dumps(
            {
                "data": {
                    "test_cert": test_cert,
                    "over_provision": over_provision,
                    "explorer_logs": explorer_logs,
                    "escalation_emails": escalation_emails,
                    "auto_extend_pools": auto_extend_pools,
                    "sort_nodes_by_sru": sort_nodes_by_sru,
                }
            }
        )

    @actor_method
    def set_developer_options(
        self,
        test_cert: bool,
        over_provision: bool,
        explorer_logs: bool,
        sort_nodes_by_sru: bool,
        escalation_emails: bool,
        auto_extend_pools: bool,
    ) -> str:
        j.core.config.set("TEST_CERT", test_cert)
        j.core.config.set("OVER_PROVISIONING", over_provision)
        j.core.config.set("EXPLORER_LOGS", explorer_logs)
        j.core.config.set("ESCALATION_EMAILS_ENABLED", escalation_emails)
        j.core.config.set("AUTO_EXTEND_POOLS_ENABLED", auto_extend_pools)
        j.core.config.set("SORT_NODES_BY_SRU", sort_nodes_by_sru)
        return j.data.serializers.json.dumps(
            {
                "data": {
                    "test_cert": test_cert,
                    "over_provision": over_provision,
                    "explorer_logs": explorer_logs,
                    "escalation_emails": escalation_emails,
                    "auto_extend_pools": auto_extend_pools,
                    "sort_nodes_by_sru": sort_nodes_by_sru,
                }
            }
        )

    @actor_method
    def clear_blocked_nodes(self) -> str:
        j.sals.reservation_chatflow.reservation_chatflow.clear_blocked_nodes()
        return j.data.serializers.json.dumps({"data": "blocked nodes got cleared successfully."})

    @actor_method
    def clear_blocked_managed_domains(self) -> str:
        j.sals.marketplace.deployer.clear_blocked_managed_domains()
        return j.data.serializers.json.dumps({"data": "blocked managed domains got cleared successfully."})

    @actor_method
    def get_email_server_config(self) -> str:
        email_server_config = j.core.config.get("EMAIL_SERVER_CONFIG", {})
        email_server_config.setdefault("host", "")
        email_server_config.setdefault("port", "")
        email_server_config.setdefault("username", "")
        email_server_config.setdefault("password", "")
        return j.data.serializers.json.dumps({"data": email_server_config})

    @actor_method
    def set_email_server_config(self, host="", port="", username="", password="") -> str:
        email_server_config = j.core.config.get("EMAIL_SERVER_CONFIG", {})
        email_server_config = {"host": host, "port": port, "username": username, "password": password}
        j.core.config.set("EMAIL_SERVER_CONFIG", email_server_config)
        return j.data.serializers.json.dumps({"data": email_server_config})

    @actor_method
    def list_escalation_emails(self) -> str:
        escalation_emails = j.core.config.get("ESCALATION_EMAILS", [])
        return j.data.serializers.json.dumps({"data": escalation_emails})

    @actor_method
    def add_escalation_email(self, email) -> str:
        escalation_emails = j.core.config.get("ESCALATION_EMAILS", [])
        if email not in escalation_emails:
            escalation_emails.append(email)
            j.core.config.set("ESCALATION_EMAILS", escalation_emails)
        return j.data.serializers.json.dumps({"data": escalation_emails})

    @actor_method
    def delete_escalation_email(self, email) -> str:
        escalation_emails = j.core.config.get("ESCALATION_EMAILS", [])
        if email in escalation_emails:
            escalation_emails.remove(email)
            j.core.config.set("ESCALATION_EMAILS", escalation_emails)
        return j.data.serializers.json.dumps({"data": escalation_emails})

    def get_notifications(self) -> str:
        notifications = []
        if j.tools.notificationsqueue.count() >= 10:
            notifications = j.tools.notificationsqueue.fetch()
        else:
            notifications = j.tools.notificationsqueue.fetch(10)
        ret = [notification.json for notification in notifications]
        return j.data.serializers.json.dumps({"data": ret})

    @actor_method
    def get_notifications_count(self) -> str:
        return j.data.serializers.json.dumps({"data": j.tools.notificationsqueue.count()})


Actor = Admin
