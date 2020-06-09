from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.god import j
from jumpscale.core.exceptions import JSException

explorers = {"main": "explorer.grid.tf", "testnet": "explorer.testnet.grid.tf"}

class Admin(BaseActor):

    @actor_method
    def admin_list(self) -> str:
        return j.data.serializers.json.dumps(
                list({'name':name} for name in j.core.identity.list_admins()))
               
    @actor_method
    def admin_add(self, name: str) -> str:
        return j.data.serializers.json.dumps(
            j.core.identity.add_admin(name))

    @actor_method
    def admin_delete(self, name: str) -> str:
        return j.data.serializers.json.dumps(
            j.core.identity.delete_admin(name))
            
    @actor_method        
    def get_current_user(self) -> str:
        try:
            cfg = j.core.identity.get_threebot_config()
            return j.data.serializers.json.dumps({
                'name': cfg['name'],
                'email': cfg['email']
            })
        except JSException as e:
            return j.data.serializers.json.dumps(str(e))

    @actor_method
    def get_explorer(self) -> str:
        config = j.core.config.get_config()

        if "explorer_url" not in config['threebot']:
            url = "https://" + explorers["testnet"] + "/explorer"
            j.clients.explorer.default_addr_set(url)
            return j.data.serializers.json.dumps(
                {"type": "testnet", "url": explorers["testnet"]})

        current_address = config['threebot']["explorer_url"].strip().lower().split("/")[2]
        if current_address == explorers["testnet"]:
            explorer_type = "testnet"
        elif current_address == explorers["main"]:
            explorer_type = "main"
        else:
            return j.data.serializers.json.dumps(
                {"type": "custom", "url": current_address})
        return j.data.serializers.json.dumps(
            {"type": explorer_type, "url": explorers[explorer_type]})

    @actor_method
    def set_explorer(self, explorer_type: str) -> str:
        if explorer_type in explorers:
            cfg = j.core.config.get("threebot")
            url = f"https://{explorers[explorer_type]}/explorer"
            client = j.clients.explorer.get(
                name=explorer_type,
                url=url)
            
            # check if we can switch with existing identity
            try:
                user = client.users.get(name=cfg["name"], email=cfg["email"])
            except j.exceptions.NotFound:
                return j.data.serializers.json.dumps(
                    f"Your identity does not exist on {explorer_type}")
            if user.pubkey != j.core.identity.nacl.get_verify_key_hex():
                return j.data.serializers.json.dumps(
                    f"Your identity does not match on {explorer_type}")
            
            j.clients.explorer.default_addr_set(url=url)

            # update our solutions
            # j.sal.reservation_chatflow.solutions_explorer_get()
            return j.data.serializers.json.dumps(
                {"type": explorer_type, "url": explorers[explorer_type]})
        return j.data.serializers.json.dumps(
                f"{explorer_type} is not a valid explorer type, must be 'testnet' or 'main'")

Actor = Admin
