from jumpscale.loader import j
from time import sleep
import uuid
import os

bad_nodes = [
    "J1Xb2piba1vZM2pSmWP24CPgREnoTce7EuUJysttCyz6",
    "A34YUGenHKyhjDMAUKZe4cVDtJM2wQ4n4XRkfGUUEYdy",
    "7Qa7fxRPtMc5R72cnNms4XWD9PJkeQJ6iD8iTU9T8p2o",
    "HYwvrxCy5z1QPALC5gTAiAMYWLH7orQ8xWEDbEyLiJV7",
    "Dko5HMMaJ9D78rAfgobA3sE29FiVrKst64v2WM4Q52gx",
    "9AcLUTkRRWGGQBn8T83Qkmuv1mwhjvmJmcvhS6r8Y8Kf",  # times out
    "HEv8cqTakrSzoxeTyauBiRNomsMFB5N2iqCfHFDY63ct",  # times out
    "J7twE8kmwkeph5WeKGcDoo1mUFgyYiWANFHtvE79L6Fp",  # times out -> about five minutes y3ne
    "FVamMByotQxr5azHA9xLoo99qP7FNi1ukysMxpm6apNG",
    "CBDY1Fu4CuxGpdU3zLL9QT5DGaRkxjpuJmzV6V5CBWg4",  # Bad access node
]
DOMAIN = "mydomain.com"
SUBDOMAIN1 = f"testa.{DOMAIN}"
SUBDOMAIN2 = f"testb.{DOMAIN}"
NETWORK_NAME = j.data.random_names.random_name()
SOLUTION_IP_ADDRESS = "172.18.4.3"
TRC1_IP_ADDRESS = "172.18.4.4"
TRC2_IP_ADDRESS = "172.18.4.5"
SOLUTION_PORT = 3001
SOLUTION_TLS_PORT = 443  # not serving https actually, but it must be provided
SECRET = f"{j.core.identity.me.tid}:{uuid.uuid4().hex}"

zos = j.sals.zos


def create_pool(currency="TFT", wallet_name="main"):
    payment_detail = zos.pools.create(cu=100, su=100, farm="freefarm", currencies=[currency])
    print(payment_detail)

    wallet = j.clients.stellar.get(wallet_name)
    txs = zos.billing.payout_farmers(wallet, payment_detail)
    pool = zos.pools.get(payment_detail.reservation_id)
    while pool.cus == 0:
        pool = zos.pools.get(payment_detail.reservation_id)
        sleep(1)

    print("compute units available:", pool.cus)
    print("storage units available:", pool.sus)
    return pool


def create_network(pool, network_name):

    ip_range = "172.18.0.0/16"

    network = zos.network.create(ip_range, network_name)
    nodes = zos.nodes_finder.nodes_by_capacity(pool_id=pool.pool_id)
    access_node = list(filter(zos.nodes_finder.filter_public_ip4, nodes))[0]
    zos.network.add_node(network, access_node.node_id, "172.18.2.0/24", pool.pool_id)
    wg_quick = zos.network.add_access(network, access_node.node_id, "172.18.3.0/24", ipv4=True)

    for workload in network.network_resources:
        wid = zos.workloads.deploy(workload)
        workload = zos.workloads.get(wid)
        while not workload.info.result.workload_id:
            sleep(1)
            workload = zos.workloads.get(wid)
    print(wg_quick)
    return network, wg_quick


def get_deploymnet_node(pool):
    available_nodes = list(zos.nodes_finder.nodes_by_capacity(cru=0, sru=0, mru=0, pool_id=pool.pool_id))
    available_nodes = [node for node in available_nodes if node.node_id not in bad_nodes]
    return available_nodes[0]


def add_node_to_network(node, network, pool):
    zos.network.add_node(network, node.node_id, "172.18.4.0/24", pool.pool_id)
    for workload in network.network_resources:
        wid = zos.workloads.deploy(workload)
        workload = zos.workloads.get(wid)
        while not workload.info.result.workload_id:
            sleep(1)
            workload = zos.workloads.get(wid)


def get_ssh_key():
    with open(os.path.expanduser("~/.ssh/id_rsa.pub"), "r") as f:
        return f.read()


def deploy_ubuntu_server(node, pool, ssh_key):
    env = {"pub_key": ssh_key, "DOMAIN": SUBDOMAIN1}

    container = zos.container.create(
        node_id=node.node_id,
        network_name=NETWORK_NAME,
        ip_address=SOLUTION_IP_ADDRESS,
        flist="https://hub.grid.tf/omar0.3bot/omarelawady-k_https_server-latest.flist",
        capacity_pool_id=pool.pool_id,
        cpu=1,
        memory=1024,
        disk_size=1024,
        entrypoint="/usr/local/bin/run_server.sh",
        env=env,
        interactive=False,
    )

    return zos.workloads.deploy(container)


def get_gateways(pool):
    gateway_ids = {g.node_id: g for g in zos.gateways_finder.gateways_search() if zos.nodes_finder.filter_is_up(g)}

    gateways = []
    for gid, g in gateway_ids.items():
        if gid in pool.node_ids:
            if not g.dns_nameserver or g.dns_nameserver == "tf-gateway-prod-05":
                continue
            gateways.append(g)

    if len(gateways) < 2:
        raise j.exceptions.Input(f"Can't find two gateways")
    return gateways[0], gateways[1]


def create_proxy(node, gateway, pool, ip_address, domain):
    reverse_proxy = zos.gateway.tcp_proxy_reverse(gateway.node_id, domain, SECRET, pool.pool_id)
    wid = zos.workloads.deploy(reverse_proxy)
    gateway_ip = j.sals.nettools.get_host_by_name(gateway.dns_nameserver[0])

    # trc container deployment
    FLIST_URL = "https://hub.grid.tf/tf-official-apps/tcprouter:latest.flist"
    secret_env = {"TRC_SECRET": zos.container.encrypt_secret(node.node_id, SECRET)}

    entrypoint = (
        f"/bin/trc -local {SOLUTION_IP_ADDRESS}:{SOLUTION_PORT} -local-tls {SOLUTION_IP_ADDRESS}:{SOLUTION_TLS_PORT}"
        f" -remote {gateway_ip}:{gateway.tcp_router_port}"
    )

    container = zos.container.create(
        node_id=node.node_id,
        network_name=NETWORK_NAME,
        ip_address=ip_address,
        flist=FLIST_URL,
        capacity_pool_id=pool.pool_id,
        entrypoint=entrypoint,
        secret_env=secret_env,
    )
    wid = zos.workloads.deploy(container)

    workload = zos.workloads.get(wid)
    while not workload.info.result.workload_id:
        sleep(1)
        workload = zos.workloads.get(wid)

    return wid


pool = create_pool()
gateway1, gateway2 = get_gateways(pool)
gateway1_ip = j.sals.nettools.get_host_by_name(gateway1.dns_nameserver[0])
gateway2_ip = j.sals.nettools.get_host_by_name(gateway2.dns_nameserver[0])
network, wg_quick = create_network(pool, NETWORK_NAME)

deployment_node = get_deploymnet_node(pool)
add_node_to_network(deployment_node, network, pool)
ssh_key = get_ssh_key()


deploy_ubuntu_server(deployment_node, pool, ssh_key)
j.logger.info(f"Reserving the proxy on the gateway {gateway1_ip}")
first_proxy = create_proxy(deployment_node, gateway1, pool, TRC1_IP_ADDRESS, SUBDOMAIN1)
j.logger.info(f"Reserving the proxy on the gateway {gateway2_ip}")
second_proxy = create_proxy(deployment_node, gateway2, pool, TRC2_IP_ADDRESS, SUBDOMAIN1)
input(f"Check https://{SUBDOMAIN1} reachable after pointing it to {gateway1_ip} in /etc/hosts")
j.logger.info(f"Decommisioning the proxy workload from the first gateway")
zos.workloads.decomission(first_proxy)
input(f"Check https://{SUBDOMAIN1} is no longer reachable.")
input(f"Check https://{SUBDOMAIN1} reachable after pointing it to {gateway2_ip} in /etc/hosts")
