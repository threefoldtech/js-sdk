"""This module is providing some helper to report stuff running on vdc

example:
  - j.tools.vdc.reporting.report_vdc_status("vdc_testnet_waleedhammam")

"""

from jumpscale.loader import j
from jumpscale.sals.zos import get as get_zos
from jumpscale.sals.vdc.vdc import VDC_WORKLOAD_TYPES
from textwrap import wrap
from jumpscale.sals.vdc.models import KubernetesRole


def _filter_vdc_workloads(vdc):
    zos = get_zos()
    user_workloads = zos.workloads.list_workloads(vdc.identity_tid)
    result = []
    for workload in user_workloads:
        if workload.info.workload_type not in VDC_WORKLOAD_TYPES:
            continue
        if not workload.info.description:
            continue
        try:
            description = j.data.serializers.json.loads(workload.info.description)
        except:
            continue
        if description.get("vdc_uuid") != vdc.solution_uuid:
            continue
        result.append(workload)
    return result


def report_vdc_status(vdc_name: str):
    """Shows all vdc workloads, nodes, status

    Args:
        vdc_name (string): target vdc to report on, None will get all values
    Returns:
        str: nice view for the vdc workloads
    """
    vdc = j.sals.vdc.find(vdc_name, load_info=True)
    if not vdc:
        print("VDC not found.")
        return

    print("\nGetting VDC information ...\n")

    zos = get_zos()
    creation_time = vdc.created.strftime("%d/%m/%Y, %H:%M:%S")
    expiration_time = "EXPIRED"
    try:
        expiration_time = vdc.expiration_date.strftime("%d/%m/%Y, %H:%M:%S")
    except:
        pass
    flavor = vdc.flavor.value
    grace_period = "Yes" if vdc.is_blocked else "No"
    master_ip = ""
    threebot_ip = ""
    threebot_domain = ""
    master_ip_state = "Down"
    threebot_domain_state = "Down"

    if vdc.has_minimal_components():
        master_ip = [n for n in vdc.kubernetes if n.role == KubernetesRole.MASTER][-1].public_ip
        threebot_ip = vdc.threebot.ip_address
        master_ip_state = "Up" if j.sals.nettools.tcp_connection_test(master_ip, 6443, 10) else "Down"
        threebot_domain = f"https://{vdc.threebot.domain}"
        threebot_domain_state = "Up" if j.sals.nettools.wait_http_test(threebot_domain, timeout=10) else "Down"

    print(
        f"Creation time: {creation_time}\n"
        f"Expiration time: {expiration_time}\n"
        f"Flavor: {flavor}\n"
        f"Grace Period:  {grace_period}\n"
        f"Master IP:  {master_ip}  --> State: {master_ip_state}\n"
        f"Threebot IP: {threebot_ip}\n"
        f"Threebot Domain: {threebot_domain}  --> State {threebot_domain_state}\n"
    )
    workloads = _filter_vdc_workloads(vdc)

    try:
        j.data.terminaltable.print_table(
            f"Wallets",
            [
                ["Name", "Address", "Balance"],
                [
                    vdc.prepaid_wallet.instance_name,
                    vdc.prepaid_wallet.address,
                    f"{vdc.prepaid_wallet.get_balance().balances[0].balance} TFT",
                ],
                [
                    vdc.provision_wallet.instance_name,
                    vdc.provision_wallet.address,
                    f"{vdc.provision_wallet.get_balance().balances[0].balance} TFT",
                ],
            ],
        )
    except:
        print("\n<== No available wallets data. Expired or invalid vdc ==>")
    print("\n")

    workloads_list = [["Wid", "Type", "State", "Farm", "PoolID", "IPv4Units", "NodeID", "NState", "Message"]]
    for workload in workloads:
        workload_type = workload.info.workload_type.name
        if not workload_type in ["Subdomain", "Reverse_proxy"]:
            farm_name = j.sals.marketplace.deployer.get_pool_farm_name(workload.info.pool_id)
            node_state = (
                "Up" if zos.nodes_finder.filter_is_up(zos._explorer.nodes.get(workload.info.node_id)) else "Down"
            )
        else:
            farm_name = "Gateway"
            node_state = "Gateway"
        workloads_list.append(
            [
                workload.id,
                workload_type,
                workload.info.next_action.name,
                farm_name,
                workload.info.pool_id,
                zos.pools.get(workload.info.pool_id).ipv4us,
                workload.info.node_id,
                node_state,
                "\n".join(wrap(workload.info.result.message, 80)),
            ]
        )
    j.data.terminaltable.print_table(f"Workloads", workloads_list)
