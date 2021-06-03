from jumpscale.sals.reservation_chatflow.deployer import DeploymentFailed
from .base_component import VDCBaseComponent
from .size import NETWORK_FARMS
import random
from jumpscale.sals.reservation_chatflow import deployer
import uuid
from jumpscale.clients.explorer.models import WorkloadType, NextAction


class VDCPublicIP(VDCBaseComponent):
    def __init__(self, vdc_deployer, farm_name):
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

    def get_public_ip(self, pool_id, node_id, solution_uuid=None):
        """
        try to reserve a public ip on network farm and returns the wid
        """
        solution_uuid = solution_uuid or uuid.uuid4().hex
        self.vdc_deployer.info(f"searching for available public ip in farm {self.farm_name}")
        for farmer_address in self.fetch_available_ips():
            address = farmer_address.address
            wid = self.get_specific_public_ip(pool_id, node_id, address, solution_uuid)
            if wid:
                return wid
            continue
        self.vdc_deployer.error(
            f"All tries to reserve a public ip failed on farm: {self.farm_name} pool: {pool_id} node: {node_id}"
        )

    def get_specific_public_ip(self, pool_id, node_id, address, solution_uuid=None):
        self.vdc_deployer.info(
            f"attempting to reserve public ip: {address} on farm: {self.farm_name} pool: {pool_id} node: {node_id}"
        )
        wid = deployer.deploy_public_ip(
            pool_id,
            node_id,
            address,
            identity_name=self.identity.instance_name,
            description=self.vdc_deployer.description,
            solution_uuid=solution_uuid,
        )
        try:
            success = deployer.wait_workload(
                wid, self.bot, 5, cancel_by_uuid=False, identity_name=self.identity.instance_name
            )
            if not success:
                raise DeploymentFailed(f"Public ip workload failed. wid: {wid}")
            return wid
        except DeploymentFailed as e:
            self.vdc_deployer.error(f"Failed to reserve public ip {address} on node {node_id} due to error {str(e)}")
