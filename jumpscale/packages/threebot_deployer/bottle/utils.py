from collections import defaultdict
from jumpscale.packages.threebot_deployer.models import USER_THREEBOT_FACTORY
from jumpscale.packages.threebot_deployer.models.user_solutions import ThreebotState
from jumpscale.clients.explorer.models import WorkloadType
from jumpscale.sals.reservation_chatflow import deployer
from jumpscale.data.serializers import json
from jumpscale.data import text
from jumpscale.loader import j


THREEBOT_WORKLOAD_TYPES = [WorkloadType.Container, WorkloadType.Subdomain, WorkloadType.Reverse_proxy]


def build_solution_info(workloads, identity_name):
    """used to build to dict containing Threebot information
    Args:
        workloads: list of workloads that makeup the threebot solution (subdomain, threebot container, trc container, reverse_proxy)
    """
    solution_info = {"wids": []}
    for workload in workloads:
        solution_info["wids"].append(workload.id)
        if workload.info.workload_type in [WorkloadType.Reverse_proxy, WorkloadType.Subdomain]:
            solution_info["domain"] = workload.domain
        elif workload.info.workload_type == WorkloadType.Container:
            decrypted_metadata = deployer.decrypt_metadata(workload.info.metadata, identity_name)
            metadata = json.loads(decrypted_metadata)
            name = metadata.get("form_info", {}).get("Solution name")
            if name:
                solution_info["name"] = name
            workload_result = json.loads(workload.info.result.data_json)
            if "trc" in workload.flist:
                solution_info["gateway_pool"] = workload.info.pool_id
                continue
            solution_info.update(
                {
                    "ipv4": workload_result["ipv4"],
                    "ipv6": workload_result["ipv6"],
                    "flist": workload.flist,
                    "disk_size": workload.capacity.disk_size,
                    "cpu": workload.capacity.cpu,
                    "memory": workload.capacity.memory,
                    "node": workload.info.node_id,
                    "compute_pool": workload.info.pool_id,
                }
            )

    return solution_info


def group_threebot_workloads_by_uuid(identity_name):
    print(identity_name)
    solutions = defaultdict(list)
    identity = j.core.identity.get(identity_name)
    zos = j.sals.zos.get(identity_name)
    for workload in zos.workloads.list(identity.tid):
        if workload.info.workload_type not in THREEBOT_WORKLOAD_TYPES:
            continue
        decrypted_metadata = deployer.decrypt_metadata(workload.info.metadata, identity_name)
        metadata = json.loads(decrypted_metadata)
        solution_uuid = metadata.get("solution_uuid")
        if not solution_uuid:
            continue
        if metadata.get("form_info", {}).get("chatflow") != "threebot":
            continue
        solutions[solution_uuid].append(workload)
    return solutions


def list_threebot_solutions(owner):
    result = []
    owner = text.removesuffix(owner, ".3bot")
    cursor, _, threebots = USER_THREEBOT_FACTORY.find_many(owner_tname=owner)
    threebots = list(threebots)
    while cursor:
        cursor, _, result = USER_THREEBOT_FACTORY.find_many(cursor, owner_tname=owner)
        threebots += list(result)
    print(threebots)
    for threebot in threebots:
        grouped_identity_workloads = group_threebot_workloads_by_uuid(threebot.identity_name)
        zos = j.sals.zos.get(threebot.identity_name)
        workloads = grouped_identity_workloads.get(threebot.solution_uuid)
        # print("Workloads", workloads)
        if not workloads:
            continue
        user_pools = {p.pool_id: p for p in zos.pools.list()}
        solution_info = build_solution_info(workloads, threebot.identity_name)
        print(solution_info)
        if "ipv4" not in solution_info or "domain" not in solution_info:
            continue
        solution_info["farm"] = threebot.farm_name
        solution_info["state"] = threebot.state.value
        solution_info["continent"] = threebot.continent
        compute_pool = user_pools.get(solution_info["compute_pool"])
        if not compute_pool:
            continue
        if threebot.state == ThreebotState.RUNNING and compute_pool.empty_at < j.data.time.utcnow().timestamp:
            solution_info["state"] = ThreebotState.STOPPED.value
        result.append(solution_info)
    return result
