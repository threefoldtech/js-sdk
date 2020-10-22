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
