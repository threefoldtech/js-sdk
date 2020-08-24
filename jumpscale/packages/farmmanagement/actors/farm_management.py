from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.clients.explorer.models import Farm
from jumpscale.loader import j


class FarmManagemenet(BaseActor):
    def __init__(self):
        super().__init__()
        self._explorer = j.core.identity.me.explorer

    @actor_method
    def update_farm(self, farm_id, farm):
        farm = Farm.from_dict(farm)
        farm.id = farm_id
        self._explorer.farms.update(farm)

    @actor_method
    def delete_node_farm(self, farm_id, node_id):
        self._explorer.farms.delete(farm_id, node_id)

    @actor_method
    def mark_node_free(self, node_id, free):
        return self._explorer.nodes.configure_free_to_use(node_id=node_id, free=free)


Actor = FarmManagemenet
