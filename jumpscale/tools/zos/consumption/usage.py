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
from jumpscale.sals.vdc.size import THREEBOT_CPU, THREEBOT_DISK, THREEBOT_MEMORY, VDC_SIZE


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
) -> float:
    """
        compute the cost of a workload over a certain period

        Args:
            workload (Union[ Container, Gateway4to6, GatewayDelegate, GatewayProxy, GatewayReverseProxy, GatewaySubdomain, K8s, NetworkResource, Volume, ZdbNamespace, ]): the workload to analyse
            duration ([int]): duration of deployment in seconds

        Returns:
            float: price in TFT
        """
    # tft_price = 0.15$
    # su_price = 10$
    # month = 3600*24*30
    # (su_prince/tft_price) / month  = 0.00002572
    compute_unit_TFT_cost_second = 0.00002572
    storage_unit_TFT_cost_second = 0.00002572
    ipv4_unit_TFT_cost_second = 0.00002572
    cu = cloud_units(workload)
    price = cu.cost(compute_unit_TFT_cost_second, storage_unit_TFT_cost_second, ipv4_unit_TFT_cost_second, duration)
    return price


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
    all_cus += sus

    # get kubernetes controller usage
    master_size = VDC_SIZE.VDC_FLAVORS[flavor]["k8s"]["controller_size"]
    k8s = K8s()
    k8s.size = master_size.value
    cus, sus, ipv4us = get_cloud_units(k8s)

    all_cus += cus
    all_sus += sus
    all_ipv4us += ipv4us

    # get kubernetes workers usage
    no_nodes = VDC_SIZE.VDC_FLAVORS[flavor]["k8s"]["no_nodes"]
    worker_size = VDC_SIZE.VDC_FLAVORS[flavor]["k8s"]["size"]
    k8s = K8s()
    k8s.size = worker_size.value
    cus, sus, ipv4us = get_cloud_units(k8s)

    all_cus += cus * (no_nodes + 1)
    all_sus += sus * (no_nodes + 1)

    # get 3bot container usage
    cont2 = Container()
    cont2.capacity.cpu = THREEBOT_CPU
    cont2.capacity.memory = THREEBOT_MEMORY
    cont2.capacity.disk_size = THREEBOT_DISK
    cont2.capacity.disk_type = DiskType.SSD
    n_cus, n_sus, _ = get_cloud_units(cont2)

    all_cus += n_cus
    all_sus += n_sus

    # create empty pool and get the payment amount
    zos = j.sals.zos.get()
    farm_name = farm_name or zos._explorer.farms.list()[0].name
    pool = zos.pools.create(round(all_cus), round(all_sus), round(all_ipv4us), farm_name)
    amount = pool.escrow_information.amount
    total_amount_dec = Decimal(amount) / Decimal(1e7)
    total_amount = "{0:f}".format(total_amount_dec)

    return total_amount
