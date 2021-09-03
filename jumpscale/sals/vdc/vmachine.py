import math
import uuid

from jumpscale.clients.explorer.models import VirtualMachine
from jumpscale.loader import j
from jumpscale.sals.reservation_chatflow import deployer, solutions
from jumpscale.sals.reservation_chatflow.deployer import DeploymentFailed

from .base_component import VDCBaseComponent
from .scheduler import CapacityChecker, Scheduler
from .size import *


class VirtualMachineDeployer(VDCBaseComponent):
    def __init__(self, *args, **kwrags) -> None:
        super().__init__(*args, **kwrags)

    def _preprare_extension_pool(self, farm_name, vm_size, duration, public_ip=False):
        """
        returns pool id after extension with enough cloud units
        duration in seconds
        """
        self.vdc_deployer.info(
            f"Preperaring pool for virtual machine on farm {farm_name}, duration: {duration}, public_ip: {public_ip}"
        )
        vmachine = VirtualMachine()
        vmachine.size = vm_size
        cloud_units = vmachine.resource_units().cloud_units()
        cus = int(cloud_units.cu * duration)
        sus = int(cloud_units.su * duration)
        ipv4us = 0
        if public_ip:
            ipv4us = int(duration)

        farm = self.explorer.farms.get(farm_name=farm_name)
        pool_id = None
        self.vdc_deployer.info(f"Vmachine extension: searching for existing pool on farm {farm_name}")
        for pool in self.zos.pools.list():
            farm_id = deployer.get_pool_farm_id(pool.pool_id, pool, self.identity.instance_name)
            if farm_id == farm.id:
                pool_id = pool.pool_id
                break

        if not pool_id:
            pool_info = self.vdc_deployer._retry_call(
                self.zos.pools.create,
                args=[math.ceil(cus), math.ceil(sus), ipv4us, farm_name, ["TFT"], j.core.identity.me],
            )
            pool_id = pool_info.reservation_id
            self.vdc_deployer.info(f"Vmachine extension: creating a new pool {pool_id}")
            self.vdc_deployer.info(f"New pool {pool_info.reservation_id} for vmachine extension.")
        else:
            self.vdc_deployer.info(f"Vmachine extension: found pool {pool_id}")
            node_ids = [node.node_id for node in self.zos.nodes_finder.nodes_search(farm_name=farm_name)]
            pool_info = self.vdc_deployer._retry_call(
                self.zos.pools.extend, args=[pool_id, cus, sus, ipv4us], kwargs={"node_ids": node_ids}
            )
            self.vdc_deployer.info(
                f"Using pool {pool_id} extension reservation: {pool_info.reservation_id} for Vmachine extension."
            )

        self.vdc_deployer.pay(pool_info)

        success = self.vdc_deployer.wait_pool_payment(pool_info.reservation_id)
        if not success:
            raise j.exceptions.Runtime(f"Pool {pool_info.reservation_id} resource reservation timedout")

        return pool_id

    def start_vmachine_deployment(
        self,
        farm_name,
        solution_name,
        query,
        vm_size,
        ssh_keys,
        enable_public_ip=False,
        solution_uuid=None,
        vmachine_type=None,
        duration=None,
    ):
        """
        search for a pool in the same farm and extend it or create a new one with the required capacity
        """
        old_node_ids = []
        for k8s_node in self.vdc_instance.kubernetes:
            old_node_ids.append(k8s_node.node_id)
        for vmachine in self.vdc_instance.vmachines:
            old_node_ids.append(vmachine.node_id)

        cc = CapacityChecker(farm_name)
        cc.exclude_nodes(*old_node_ids)

        if not cc.add_query(**query):
            raise j.exceptions.Validation(f"Not enough capacity in farm {farm_name} for deploying vmachine")

        duration = (
            duration if duration else self.vdc_instance.expiration_date.timestamp() - j.data.time.utcnow().timestamp
        )
        if duration <= 0:
            raise j.exceptions.Validation(f"invalid duration {duration}")

        scheduler = Scheduler(farm_name=farm_name)
        scheduler.exclude_nodes(*old_node_ids)
        nodes_generator = scheduler.nodes_by_capacity(**query, public_ip=enable_public_ip)

        pool_id = self._preprare_extension_pool(farm_name, vm_size, duration, enable_public_ip)

        network_view = deployer.get_network_view(self.vdc_name, identity_name=self.identity.instance_name)

        vm_res = self.deploy_vmachine(
            solution_name,
            vm_size,
            pool_id,
            nodes_generator,
            ssh_keys,
            solution_uuid,
            network_view,
            enable_public_ip,
            vmachine_type,
            description=self.vdc_deployer.description,
        )
        if not vm_res:
            self.vdc_deployer.error(f"Failed to deploy vmachine")
            raise j.exceptions.Runtime(f"Failed to deploy vmachine")
        return vm_res

    def deploy_vmachine(
        self,
        solution_name,
        vm_size,
        pool_id,
        nodes_generator,
        ssh_keys,
        solution_uuid,
        network_view,
        enable_public_ip,
        vmachine_type,
        description="",
    ):
        vmachine_ip = None
        while not vmachine_ip:
            try:
                try:
                    vmachine_node = next(nodes_generator)
                except StopIteration:
                    return
                self.vdc_deployer.info(f"Deploying virtual machine on node {vmachine_node.node_id}")
                # add node to network
                try:
                    result = deployer.add_network_node(
                        self.vdc_name, vmachine_node, pool_id, network_view, self.bot, self.identity.instance_name
                    )
                    if result:
                        for wid in result["ids"]:
                            success = deployer.wait_workload(
                                wid, self.bot, 3, identity_name=self.identity.instance_name, cancel_by_uuid=False
                            )
                            if not success:
                                self.vdc_deployer.error(f"Failed to deploy network for virtual machine")
                                raise DeploymentFailed
                except DeploymentFailed:
                    self.vdc_deployer.error(
                        f"Failed to deploy network for virtual machine on node {vmachine_node.node_id}"
                    )
                    continue
            except IndexError:
                self.vdc_deployer.error("All attempts to deploy virtual machine on nodes node have been failed")
                raise j.exceptions.Runtime("All attempts to deploy virtual machine on nodes node have been failed")

            network_view = network_view.copy()
            private_ip_address = network_view.get_free_ip(vmachine_node)

            self.vdc_deployer.info(f"Virtual machine ip: {private_ip_address}")

            metadata = {"form_info": {"chatflow": "vmachine", "name": solution_name, "solution_uuid": solution_uuid}}
            wid, public_ip = deployer.deploy_vmachine(
                node_id=vmachine_node.node_id,
                network_name=network_view.name,
                name=vmachine_type,
                ip_address=private_ip_address,
                ssh_keys=ssh_keys,
                pool_id=pool_id,
                size=vm_size,
                enable_public_ip=enable_public_ip,
                description=description,
                **metadata,
            )
            self.vdc_deployer.info(f"virtual machine machine wid: {wid}")
            try:
                success = deployer.wait_workload(
                    wid, self.bot, identity_name=self.identity.instance_name, cancel_by_uuid=False
                )
                if not success:
                    raise DeploymentFailed()
                return {"public_ip": public_ip, "ip_address": private_ip_address, "vm_wid": wid}
            except DeploymentFailed:
                if enable_public_ip:
                    self.zos.workloads.decomission(self.zos.workloads.get(wid).public_ip)
                self.vdc_deployer.error(f"Failed to deploy virtual machine wid: {wid}")
                continue
        self.vdc_deployer.error(f"All attempts to deploy virtual machine have failed")
