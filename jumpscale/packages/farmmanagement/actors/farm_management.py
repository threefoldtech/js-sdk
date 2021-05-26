from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.clients.explorer.models import Farm
from jumpscale.loader import j

import requests


class FarmManagemenet(BaseActor):
    def __init__(self):
        super().__init__()

    @property
    def _explorer(self):
        return j.core.identity.me.explorer

    @actor_method
    def update_farm(self, farm_id, farm):
        try:
            farm = Farm.from_dict(farm)
            farm.id = farm_id
            self._explorer.farms.update(farm)
        except requests.exceptions.HTTPError as e:
            raise j.exceptions.NotFound(str(e))

    @actor_method
    def delete_node_farm(self, farm_id, node_id):
        self._explorer.farms.delete(farm_id, node_id)

    @actor_method
    def mark_node_free(self, node_id, free):
        return self._explorer.nodes.configure_free_to_use(node_id=node_id, free=free)

    @actor_method
    def list_farms(self, user_id) -> str:
        farms = [f.to_dict() for f in self._explorer.farms.list(user_id)]
        for farm in farms:
            farm["explorer_prices"] = self._explorer.farms.get_explorer_prices()
        return j.data.serializers.json.dumps(farms)

    @actor_method
    def get_farm(self, farm_id) -> str:
        farm = self._explorer.farms.get(farm_id).to_dict()
        farm["explorer_prices"] = self._explorer.farms.get_explorer_prices()
        return j.data.serializers.json.dumps(farm)

    @actor_method
    def add_ip_addresses(self, farm_id, ip_addresses):
        return self._explorer.farms.add_public_ips(farm_id, ip_addresses)

    @actor_method
    def remove_ip_addresses(self, farm_id, ip_addresses):
        return self._explorer.farms.remove_public_ips(farm_id, ip_addresses)

    @actor_method
    def enable_farm_default_prices(self, farm_id, prices) -> str:
        return j.data.serializers.json.dumps({"data": self._explorer.farms.enable_custom_farm_prices(farm_id, prices)})

    @actor_method
    def get_deals(self, farm_id) -> str:
        return j.data.serializers.json.dumps({"data": self._explorer.farms.get_deals(farm_id)})

    @actor_method
    def get_deals_with_threebot_names(self, farm_id) -> str:
        custom_prices = self._explorer.farms.get_deals(farm_id)
        for cp in custom_prices:
            try:
                cp["threebot_name"] = self._explorer.users.get(cp["threebot_id"]).name
            except:
                cp["threebot_name"] = "UNKNOWN_USER"
        return j.data.serializers.json.dumps({"data": custom_prices})

    @actor_method
    def get_explorer_prices(self) -> str:
        return j.data.serializers.json.dumps({"data": self._explorer.farms.get_explorer_prices()})

    @actor_method
    def get_deal_for_threebot(self, farm_id, threebot_id) -> str:
        return j.data.serializers.json.dumps({"data": self._explorer.farms.get_deal_for_threebot(farm_id, threebot_id)})

    @actor_method
    def create_or_update_deal_for_threebot_by_name(self, farm_id, threebot_name, custom_prices) -> str:
        threebot_id = self._explorer.users.get(name=threebot_name).id
        return j.data.serializers.json.dumps(
            {"data": self._explorer.farms.create_or_update_deal_for_threebot(farm_id, threebot_id, custom_prices)}
        )

    @actor_method
    def create_or_update_deal_for_threebot(self, farm_id, threebot_id, custom_prices) -> str:
        return j.data.serializers.json.dumps(
            {"data": self._explorer.farms.create_or_update_deal_for_threebot(farm_id, threebot_id, custom_prices)}
        )

    @actor_method
    def list_nodes(self, farm_id) -> str:
        return j.data.serializers.json.dumps([f.to_dict() for f in self._explorer.nodes.list(farm_id)])

    @actor_method
    def register_farm(self, farm) -> str:
        return j.data.serializers.json.dumps({"data": self._explorer.farms.register_farm_dict(farm)})

    @actor_method
    def delete_deal(self, farm_id, threebot_id) -> str:
        return j.data.serializers.json.dumps({"data": self._explorer.farms.delete_deal(farm_id, threebot_id)})


Actor = FarmManagemenet
