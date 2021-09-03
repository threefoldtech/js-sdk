from decimal import Decimal
from typing import Union

from jumpscale.clients.explorer.models import (
    CloudUnits,
    Container,
    DiskType,
    Gateway4to6,
    GatewayDelegate,
    GatewayProxy,
    GatewayReverseProxy,
    GatewaySubdomain,
    K8s,
    NetworkResource,
    NextAction,
    ResourceUnitAmount,
    Volume,
    ZdbNamespace,
)
from jumpscale.loader import j
from jumpscale.sals.vdc.size import (
    THREEBOT_CPU,
    THREEBOT_DISK,
    THREEBOT_MEMORY,
    VDC_SIZE,
    ETCD_CLUSTER_SIZE,
    ETCD_DISK,
    ETCD_CPU,
    ETCD_MEMORY,
)


def cloud_units(
    workload: Union[
        Container,
        Gateway4to6,
        GatewayDelegate,
        GatewayProxy,
        GatewayReverseProxy,
        GatewaySubdomain,
        K8s,
        NetworkResource,
        Volume,
        ZdbNamespace,
    ]
) -> CloudUnits:
    """
    Compute the amount of cloud units consumed by second  workload

    Args:
        workload (Union[ Container, Gateway4to6, GatewayDelegate, GatewayProxy, GatewayReverseProxy, GatewaySubdomain, K8s, NetworkResource, Volume, ZdbNamespace, ]): [description]

    Returns:
        CloudUnits: the amount of cloud units consumed by second by the workload
    """
    ru = workload.resource_units()
    return ru.cloud_units()


def cost(
    workload: Union[
        Container,
        Gateway4to6,
        GatewayDelegate,
        GatewayProxy,
        GatewayReverseProxy,
        GatewaySubdomain,
        K8s,
        NetworkResource,
        Volume,
        ZdbNamespace,
    ],
    duration,
    farm_id,
) -> float:
    """
        compute the cost of a workload over a certain period

        Args:
            workload (Union[ Container, Gateway4to6, GatewayDelegate, GatewayProxy, GatewayReverseProxy, GatewaySubdomain, K8s, NetworkResource, Volume, ZdbNamespace, ]): the workload to analyse
            duration ([int]): duration of deployment in seconds

        Returns:
            float: price in TFT
    """
    cu = cloud_units(workload)
    zos = j.sals.zos.get()
    farm_prices = zos._explorer.farms.get_deal_for_threebot(farm_id, j.core.identity.me.tid)["custom_cloudunits_price"]
    price = zos._explorer.prices.calculate(cus=cu.cu, sus=cu.su, ipv4us=cu.ipv4u, farm_prices=farm_prices)
    return price * duration


def calculate_vdc_price(flavor, farm_name=None):
    """calculate the workloads price for vdcs in TFT

    Args:
        flavor (str): vdc flavor in [silver, gold, platinum, diamond]

    Returns:
        str: vdc price
    """
    all_cus = 0
    all_sus = 0
    all_ipv4us = 0

    # get the flavor enum
    for item in VDC_SIZE.VDC_FLAVORS.keys():
        if flavor == item.value:
            flavor = item

    # calculate cloud units enough for a month
    def get_cloud_units(workload):
        ru = workload.resource_units()
        cloud_units = ru.cloud_units()
        return (
            cloud_units.cu * 60 * 60 * 24 * 30,
            cloud_units.su * 60 * 60 * 24 * 30,
            cloud_units.ipv4u * 60 * 60 * 24 * 30,
        )

    # get zdbs usage
    zdb = ZdbNamespace()
    zdb.size = VDC_SIZE.S3_ZDB_SIZES[VDC_SIZE.VDC_FLAVORS[flavor]["s3"]["size"]]["sru"]
    zdb.disk_type = DiskType.HDD
    _, sus, _ = get_cloud_units(zdb)
    all_sus += sus

    # get kubernetes controller usage
    master_size = VDC_SIZE.VDC_FLAVORS[flavor]["k8s"]["controller_size"]
    k8s = K8s()
    k8s.size = master_size.value
    cus, sus, ipv4us = get_cloud_units(k8s)

    all_cus += cus
    all_sus += sus
    all_ipv4us += 60 * 60 * 24 * 30  # hardcoded since not calculated in the explorer client

    # get kubernetes workers usage
    no_nodes = VDC_SIZE.VDC_FLAVORS[flavor]["k8s"]["no_nodes"]
    worker_size = VDC_SIZE.VDC_FLAVORS[flavor]["k8s"]["size"]
    k8s = K8s()
    k8s.size = worker_size.value
    cus, sus, ipv4us = get_cloud_units(k8s)

    all_cus += cus * (no_nodes)
    all_sus += sus * (no_nodes)

    # get 3bot container usage
    cont2 = Container()
    cont2.capacity.cpu = THREEBOT_CPU
    cont2.capacity.memory = THREEBOT_MEMORY
    cont2.capacity.disk_size = THREEBOT_DISK
    cont2.capacity.disk_type = DiskType.SSD
    n_cus, n_sus, _ = get_cloud_units(cont2)

    all_cus += n_cus
    all_sus += n_sus

    # etcd containers usage
    etcd_cont = Container()
    etcd_cont.capacity.cpu = ETCD_CPU
    etcd_cont.capacity.memory = ETCD_MEMORY
    etcd_cont.capacity.disk_size = ETCD_DISK
    etcd_cont.capacity.disk_type = DiskType.SSD
    n_cus, n_sus, _ = get_cloud_units(etcd_cont)

    all_cus += n_cus * ETCD_CLUSTER_SIZE
    all_sus += n_sus * ETCD_CLUSTER_SIZE

    zos = j.sals.zos.get()
    farm_prices = zos._explorer.farms.get_deal_for_threebot(1, j.core.identity.me.tid)["custom_cloudunits_price"]
    total_amount = zos._explorer.prices.calculate(cus=all_cus, sus=all_sus, ipv4us=all_ipv4us, farm_prices=farm_prices)
    total_amount = round(total_amount, 6)
    return total_amount
