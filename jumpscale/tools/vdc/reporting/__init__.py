"""This module is providing some helper to report stuff running on vdc

example:
  - j.tools.vdc.reporting.report_vdc_status("vdc_testnet_waleedhammam")

"""

from jumpscale.loader import j
from jumpscale.sals.zos import get as get_zos
from jumpscale.sals.vdc.vdc import VDC_WORKLOAD_TYPES
from textwrap import wrap


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
    print("\nGetting VDC information ...")
    vdc = j.sals.vdc.find(vdc_name, load_info=True)
    zos = get_zos()
    creation_time = vdc.created.strftime("%d/%m/%Y, %H:%M:%S")
    expiration_time = vdc.expiration_date.strftime("%d/%m/%Y, %H:%M:%S")
    flavor = vdc.flavor.value
    grace_period = "Yes" if vdc.is_blocked else "No"
    master_ip = ""
    threebot_ip = ""
    if vdc.has_minimal_components():
        master_ip = vdc.kubernetes[0].public_ip
        threebot_ip = vdc.threebot.ip_address

    print(
        f"Creation time: {creation_time}\n"
        f"Expiration time: {expiration_time}\n"
        f"Flavor: {flavor}\n"
        f"Grace Period:  {grace_period}\n"
        f"Master IP:  {master_ip}\n"
        f"Threebot IP: {threebot_ip}\n"
    )
    workloads = _filter_vdc_workloads(vdc)

    print_list = [["Wid", "Type", "Next Action", "Farm", "Pool ID", "Node ID", "Node State", "Message"]]
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
        print_list.append(
            [
                workload.id,
                workload_type,
                workload.info.next_action.name,
                farm_name,
                workload.info.pool_id,
                workload.info.node_id,
                node_state,
                "\n".join(wrap(workload.info.result.message, 80)),
            ]
        )
    j.data.terminaltable.print_table(f"\nWorkloads", print_list)