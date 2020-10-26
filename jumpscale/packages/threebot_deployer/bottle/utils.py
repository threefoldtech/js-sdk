import time
from collections import defaultdict
from decimal import Decimal
from jumpscale.sals.marketplace import solutions
from jumpscale.packages.threebot_deployer.models import USER_THREEBOT_FACTORY
from jumpscale.packages.threebot_deployer.models.user_solutions import ThreebotState
from jumpscale.clients.explorer.models import WorkloadType, NextAction
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
    solutions = defaultdict(list)
    identity = j.core.identity.get(identity_name)
    zos = j.sals.zos.get(identity_name)
    for workload in zos.workloads.list(identity.tid):
        if workload.info.workload_type not in THREEBOT_WORKLOAD_TYPES or not workload.info.metadata:
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
    for threebot in threebots:
        grouped_identity_workloads = group_threebot_workloads_by_uuid(threebot.identity_name)
        zos = j.sals.zos.get(threebot.identity_name)
        workloads = grouped_identity_workloads.get(threebot.solution_uuid)
        if not workloads:
            continue
        user_pools = {p.pool_id: p for p in zos.pools.list()}
        solution_info = build_solution_info(workloads, threebot.identity_name)
        if "ipv4" not in solution_info or "domain" not in solution_info:
            continue
        solution_info["solution_uuid"] = threebot.solution_uuid
        solution_info["farm"] = threebot.farm_name
        solution_info["state"] = threebot.state.value
        solution_info["continent"] = threebot.continent
        compute_pool = user_pools.get(solution_info["compute_pool"])
        if not compute_pool:
            continue
        if threebot.state == ThreebotState.RUNNING and compute_pool.empty_at == 9223372036854775807:
            solution_info["state"] = ThreebotState.STOPPED.value
            threebot.state = ThreebotState.STOPPED
            threebot.save()
        result.append(solution_info)
    return result


def get_threebot_workloads_by_uuid(solution_uuid, identity_name):
    result = []
    workloads = solutions.get_workloads_by_uuid(solution_uuid, NextAction.DEPLOY, identity_name=identity_name)
    for workload in workloads:
        decrypted_metadata = deployer.decrypt_metadata(workload.info.metadata, identity_name)
        metadata = json.loads(decrypted_metadata)
        if metadata.get("form_info", {}).get("chatflow") != "threebot":
            continue
        result.append(workload)
    return result


def get_threebot_config_instance(owner, solution_uuid):
    owner = text.removesuffix(owner, ".3bot")
    threebot = USER_THREEBOT_FACTORY.find(f"threebot_{solution_uuid}")
    if not threebot:
        raise j.exceptions.NotFound(f"Threebot with uuid {solution_uuid} does not exist")
    if threebot.owner_tname != owner:
        raise j.exceptions.Permission(f"user {owner} does not own threebot with uuid {solution_uuid}")
    return threebot


def stop_threebot_solution(owner, solution_uuid):
    owner = text.removesuffix(owner, ".3bot")
    threebot = get_threebot_config_instance(owner, solution_uuid)
    zos = j.sals.zos.get(threebot.identity_name)
    solution_workloads = get_threebot_workloads_by_uuid(solution_uuid, threebot.identity_name)
    for workload in solution_workloads:
        zos.workloads.decomission(workload.id)
    threebot.state = ThreebotState.STOPPED
    threebot.save()
    return threebot


def delete_threebot_solution(owner, solution_uuid):
    threebot = stop_threebot_solution(owner, solution_uuid)
    threebot_name = threebot.name
    status = "Failed to destroy backups, 3Bot name doesn't exist"
    ssh_server1 = j.clients.sshclient.get("backup_server1")
    ssh_server2 = j.clients.sshclient.get("backup_server2")
    try:
        ssh_server1.sshclient.run(
            f"cd ~/backup; htpasswd -D  .htpasswd {threebot_name}; cd /home/backup_config; rm -r {threebot_name}"
        )
        ssh_server2.sshclient.run(
            f"cd ~/backup; htpasswd -D  .htpasswd {threebot_name}; cd /home/backup_config; rm -r {threebot_name}"
        )
    except:
        raise j.exceptions.Value(status)
    threebot.state = ThreebotState.DELETED
    threebot.save()
    return threebot

