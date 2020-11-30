from .base_component import VDCBaseComponent
from .size import NETWORK_FARM
import random


class VDCPublicIP(VDCBaseComponent):
    def __init__(self, vdc_deployer, farm_name=NETWORK_FARM):
        super().__init__(vdc_deployer)
        self.farm_name = farm_name
        self._farm = None

    @property
    def farm(self):
        if not self._farm:
            self._farm = self.explorer.farms.get(farm_name=self.farm_name)
        return self._farm

    def fetch_available_ips(self):
        addresses = [address for address in self.farm.ipaddresses if not address.reservation_id]
        random.shuffle(addresses)
        return addresses

    def get_public_ip(self, node_id):
        """
        try to reserve a public ip on network farm and returns the wid
        """
        for address in self.fetch_available_ips():
            pass
