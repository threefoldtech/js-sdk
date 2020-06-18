from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.clients.explorer.models import TfgridDirectoryFarm1
from jumpscale.god import j

class FarmManagemenet(BaseActor):
    def __init__(self):
        self._explorer = j.clients.explorer.get_default()

    @actor_method
    def update_farm(self, farm_id, farm):
        farm = TfgridDirectoryFarm1()
        farm["id"] = farm_id
        self._explorer.farms.update(farm)

    @actor_method
    def mark_node_free(self, node_id, free):
        return self._explorer.nodes.configure_free_to_use(node_id=node_id, free=free)

Actor = FarmManagemenet