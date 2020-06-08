from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.god import j

explorers = {"main": "explorer.grid.tf", "testnet": "explorer.testnet.grid.tf"}

class Admin(BaseActor):

    @actor_method
    def admin_list(self) -> str:
        return "hello from admin_list actor"

    @actor_method
    def admin_add(self, name: str) -> str:
        return "hello from admin_add actor"

    @actor_method
    def admin_delete(self, name: str) -> str:
        return "hello from admin_delete actor"

    @actor_method
    def get_explorer(self) -> str:
        """
        Get current explorer (testnet/main)
        """

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
            client = j.clients.explorer.get(
                name=explorer_type,
                url=f"https://{explorers[explorer_type]}/explorer")
            
            # check if we can switch with existing identity
            try:
                user = client.users.get(name=cfg["name"], email=cfg["email"])
            except j.exceptions.NotFound:
                return j.data.serializers.json.dumps(
                    f"Your identity does not exists on {explorer_type}")
            if user.pubkey != j.core.identity.nacl.get_verify_key_hex():
                return j.data.serializers.json.dumps(
                    f"Your identity does not match on {explorer_type}")
            
            # cfg["id"] = user.id
            j.clients.explorer.default_addr_set(explorers[explorer_type])

            # update our solutions
            # j.sal.reservation_chatflow.solutions_explorer_get()
            return j.data.serializers.json.dumps(
                {"type": explorer_type, "url": explorers[explorer_type]})
        return j.data.serializers.json.dumps(
                f"{explorer_type} is not a valid explorer type, must be 'testnet' or 'main'")

Actor = Admin
