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


def get_payment_amount(pool):
    escrow_info = pool.escrow_information
    resv_id = pool.reservation_id
    escrow_address = escrow_info.address
    escrow_asset = escrow_info.asset
    total_amount = escrow_info.amount
    if not total_amount:
        return
    total_amount_dec = Decimal(total_amount) / Decimal(1e7)
    total_amount = "{0:f}".format(total_amount_dec)
    return resv_id, escrow_address, escrow_asset, total_amount


# TODO we need to find when this pool is going to expire(filter the pools that are less then 2 weeks to expire)


def pay_pool(pool_info):
    # Get the amount of payment
    resv_id, escrow_address, escrow_asset, total_amount = get_payment_amount(pool_info)
    # Get the user wallets
    wallets = j.sals.reservation_chatflow.reservation_chatflow.list_wallets()
    for wallet in wallets:
        try:
            wallet.transfer(
                destination_address=escrow_address, amount=total_amount, asset=escrow_asset, memo_text=f"p-{resv_id}"
            )
            return True
        except:
            pass
    return False


def check_pool_expiration(pool):
    remaining_days = (pool.empty_at - time.time()) / 86400  # converting seconds to days
    if remaining_days < 14 and remaining_days > 0:
        return True
    return False


def calculate_pool_units(pool, days=14):
    cu = pool.active_cu * 60 * 60 * 24 * days
    su = pool.active_su * 60 * 60 * 24 * days
    return cu, su


def auto_extend_pools():
    pools = j.sals.zos.get().pools.list()
    for pool in pools:
        import pdb

        pdb.set_trace()
        if check_pool_expiration(pool):
            cu, su = calculate_pool_units(pool)
            auto_extend_pool(pool.pool_id, cu, su)


def auto_extend_pool(pool_id, cu, su, currencies=["TFT"]):
    try:
        pool_info = j.sals.zos.get().pools.extend(pool_id, cu, su, currencies=currencies)
    except Exception as e:
        raise j.exceptions.Runtime(f"Error happend during extending the pool, {str(e)}")
    if not pay_pool(pool_info):
        send_mail(pool_info)


def send_mail(pool_info, sender=""):
    """
    This method send mail in case the auto extend fail
    """
    recipients_emails = []
    user_mail = j.core.identity.me.email
    recipients_emails.append(user_mail)
    escalation_emails = j.core.config.get("ESCALATION_EMAILS")
    recipients_emails.extend(escalation_emails)
    mail = j.clients.mail.get("mail")
    mail.smtp_server = "localhost"
    mail.smtp_port = "1025"
    mail.send(recipients_emails, sender=sender, message="We are not apple to extend")

