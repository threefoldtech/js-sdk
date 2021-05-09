from jumpscale.loader import j

from jumpscale.sals.vdc.models import KubernetesRole
from jumpscale.tools.servicemanager.servicemanager import BackgroundService


class BandwidthLimitService(BackgroundService):
    def __init__(self, interval=2 * 60 * 60, *args, **kwargs):
        super().__init__(interval, *args, **kwargs)

    def job(self):
        j.logger.debug("Bandwith Limit service started.")
        if "testnet" not in j.core.identity.me.explorer_url:
            return
        vdc_name = j.sals.vdc.list_all().pop()
        vdc = j.sals.vdc.get(vdc_name)
        vdc.load_info()
        cmds = """
        sudo tc qdisc del dev {iface} root
        sudo tc qdisc add dev {iface} handle 1: root htb default 11
        sudo tc class add dev {iface} parent 1: classid 1:1 htb rate 10mbit
        sudo tc class add dev {iface} parent 1:1 classid 1:11 htb rate 10mbit
        sudo tc qdisc add dev {iface} parent 1:11 handle 10: netem delay 200ms
        """
        for node in vdc.kubernetes:
            iface = "eth0"
            if node.public_ip != "::/128":
                iface = "eth1"
            j.logger.debug(f"Applying bandwidth limit on kubernetes node {node.wid} with address {node.ip_address}")
            ssh_client = vdc.get_ssh_client(name=str(node.wid), ip_address=node.ip_address, user="rancher")
            rc, _, err = ssh_client.sshclient.run(cmds.format(iface=iface), warn=True)
            if rc:
                j.logger.error(
                    f"Failed to apply bandwidth limit on node {node.wid} with address {node.ip_address} due to error: {err}"
                )


service = BandwidthLimitService()
