from typing import Union

from jumpscale.clients.explorer.models import (
    CloudUnits,
    Container,
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
    cu = cloud_units(workload)
    price = cu.cost(compute_unit_TFT_cost_second, storage_unit_TFT_cost_second, duration)
    return price
