from io import StringIO

from jumpscale.sals.zos3.workload import Workload
from jumpscale.sals.zos3.workload.network import Peer, Network


def test_network():
    peer = Peer(subnet="10.100.0.0", wireguard_public_key="aa", allowed_ips=["10.100.0.1"])
    net = Network(
        name="test",
        ip_range="10.100.0.0/16",
        subnet="10.100.0.0/16",
        wireguard_private_key_encrypted="xx",
        wireguard_listen_port=5522,
        peers=[peer],
        endpoint="",
        works=["abcdef"],
    )

    w = Workload(user_id="test",)
    w.data = net
    print(w.signature)
