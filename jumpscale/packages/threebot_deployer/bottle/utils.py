from jumpscale.sals.chatflows.chatflows import StopChatFlow
import uuid
from jumpscale.sals.marketplace import solutions
from jumpscale.sals.reservation_chatflow.deployer import (
    deployment_context,
    DeploymentFailed,
)
from jumpscale.packages.threebot_deployer.models import (
    USER_THREEBOT_FACTORY,
    BACKUP_MODEL_FACTORY,
)
from jumpscale.packages.threebot_deployer.models.user_solutions import ThreebotState
from jumpscale.clients.explorer.models import WorkloadType, NextAction
from jumpscale.sals.marketplace import deployer
from jumpscale.data.serializers import json
from jumpscale.data import text
from jumpscale.loader import j
from jumpscale.data.nacl.jsnacl import NACL
from contextlib import ContextDecorator


THREEBOT_WORKLOAD_TYPES = [
    WorkloadType.Container,
    WorkloadType.Subdomain,
    WorkloadType.Reverse_proxy,
]


class threebot_identity_context(ContextDecorator):
    def __init__(self, identity_name):
        self.identity_name = identity_name

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        j.core.identity.delete(self.identity_name)


def build_solution_info(workloads, threebot):
    """used to build to dict containing Threebot information
    Args:
        workloads: list of workloads that makeup the threebot solution (subdomain, threebot container, trc container, reverse_proxy)
    """
    solution_info = {"wids": [], "name": threebot.name}
    for workload in workloads:
        solution_info["wids"].append(workload.id)
        if workload.info.workload_type in [
            WorkloadType.Reverse_proxy,
            WorkloadType.Subdomain,
        ]:
            solution_info["domain"] = workload.domain
            solution_info["gateway_pool"] = workload.info.pool_id
            solution_info["gateway"] = workload.info.node_id
        elif workload.info.workload_type == WorkloadType.Container:
            workload_result = json.loads(workload.info.result.data_json)
            if "trc" in workload.flist:
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
                    "network": workload.network_connection[0].network_id,
                    "branch": workload.environment.get("SDK_VERSION"),
                    "public_key": workload.environment.get("SSHKEY"),
                }
            )

    return solution_info


def group_threebot_workloads_by_uuid(threebot, zos):
    solutions = {threebot.solution_uuid: []}
    threebot_wids = [
        threebot.threebot_container_wid,
        threebot.trc_container_wid,
        threebot.subdomain_wid,
        threebot.reverse_proxy_wid,
    ]
    for workload in zos.workloads.list(threebot.identity_tid):
        if workload.id in threebot_wids:
            solutions[threebot.solution_uuid].append(workload)
    return solutions


def get_threebot_zos(threebot):
    _, _, listing_identities = j.core.identity.find_many(explorer_url=threebot.explorer_url)
    listing_identity = list(listing_identities)[0]
    zos = j.sals.zos.get(listing_identity.instance_name)
    return zos


def list_threebot_solutions(owner):
    result = []
    owner = text.removesuffix(owner, ".3bot")
    cursor, _, threebots = USER_THREEBOT_FACTORY.find_many(owner_tname=owner)
    threebots = list(threebots)
    while cursor:
        cursor, _, result = USER_THREEBOT_FACTORY.find_many(cursor, owner_tname=owner)
        threebots += list(result)
    for threebot in threebots:
        zos = get_threebot_zos(threebot)
        grouped_identity_workloads = group_threebot_workloads_by_uuid(threebot, zos)
        workloads = grouped_identity_workloads.get(threebot.solution_uuid)
        if not workloads:
            continue
        solution_info = build_solution_info(workloads, threebot)
        if "ipv4" not in solution_info or "domain" not in solution_info:
            continue
        solution_info["solution_uuid"] = threebot.solution_uuid
        solution_info["farm"] = threebot.farm_name
        solution_info["state"] = threebot.state.value
        solution_info["continent"] = threebot.continent
        compute_pool = zos.pools.get(solution_info["compute_pool"])
        solution_info["expiration"] = compute_pool.empty_at
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
    workloads = solutions.get_workloads_by_uuid(solution_uuid, identity_name=identity_name)
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


def generate_user_identity(threebot, password, zos):
    identity_tid = threebot.identity_tid
    user = zos._explorer.users.get(identity_tid)
    words = j.data.encryption.key_to_mnemonic(password.encode().zfill(32))
    seed = j.data.encryption.mnemonic_to_key(words)
    pubkey = NACL(seed).get_verify_key_hex()
    if pubkey != user.pubkey:
        raise j.exceptions.Permission("Invalid Password")
    suffix = "main"
    if "testnet" in threebot.explorer_url:
        suffix = "test"
    identity_name = f"{user.name}_{suffix}"
    identity = j.core.identity.get(
        identity_name, tname=user.name, email=user.email, words=words, explorer_url=threebot.explorer_url,
    )
    identity.register()
    identity.save()
    return identity


def stop_threebot_solution(owner, solution_uuid, password):
    owner = text.removesuffix(owner, ".3bot")
    threebot = get_threebot_config_instance(owner, solution_uuid)
    if not threebot.verify_secret(password):
        raise j.exceptions.Validation(f"incorrect secret provided")
    zos = get_threebot_zos(threebot)
    identity = generate_user_identity(threebot, password, zos)
    zos = j.sals.zos.get(identity.instance_name)
    with threebot_identity_context(identity.instance_name):
        solution_workloads = get_threebot_workloads_by_uuid(solution_uuid, identity.instance_name)
        for workload in solution_workloads:
            if workload.info.next_action == NextAction.DEPLOY:
                zos.workloads.decomission(workload.id)
        threebot.state = ThreebotState.STOPPED
        threebot.save()
    return threebot


def delete_threebot_solution(owner, solution_uuid, password):
    threebot = stop_threebot_solution(owner, solution_uuid, password)
    threebot_name = threebot.name
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
        j.logger.warning(f"Couldn't find backup for uuid {solution_uuid} and owner {owner}")
    threebot.state = ThreebotState.DELETED
    threebot.save()
    return threebot


def redeploy_threebot_solution(
    owner,
    solution_uuid,
    backup_password,
    compute_pool_id=None,
    gateway_pool_id=None,
    solution_info=None,
    node_id=None,
    bot=None,
    retry=False,
    prompt_retry_only=True,
):
    """
    Args:
        owner (str): threebot_name of the logged in user
        solution_uuid (str): of the not-running threebot that needs to be started
        compute_pool_id (str): to override the pool id used for container deployment. if not specified, it will use the old pool id
        gateway_pool_id (str): to override the pool id used for subdomain and proxy deployment. if not specified, it will use the old pool id. (should override the subdomain specified in solution_info)
        solution_info (dict): to override the information used in deployment. if any key is not specified, it will use the old value
    """
    if prompt_retry_only:
        msg_bot = None
    else:
        msg_bot = bot
    retries = 3 if retry else 1
    solution_info = solution_info or {}
    owner = text.removesuffix(owner, ".3bot")
    j.logger.debug(f"Fetching solution info for uuid {solution_uuid} and owner {owner}")
    while retries:
        try:
            if bot:
                bot.md_show_update("Starting your 3Bot...")
            threebot = get_threebot_config_instance(owner, solution_uuid)
            if not threebot.verify_secret(backup_password):
                raise j.exceptions.Validation(f"incorrect secret provided")
            zos = get_threebot_zos(threebot)
            identity = generate_user_identity(threebot, backup_password, zos)
            with threebot_identity_context(identity.instance_name):
                j.logger.debug(f"Using identity {identity.instance_name}")
                with deployment_context():
                    zos = j.sals.zos.get(identity.instance_name)
                    solution_workloads = get_threebot_workloads_by_uuid(solution_uuid, identity.instance_name)
                    new_solution_info = build_solution_info(solution_workloads, threebot)
                    j.logger.debug(f"old solution info: {new_solution_info}")
                    new_solution_info.update(solution_info)
                    j.logger.debug(f"updated solution info: {new_solution_info}")
                    gateway_pool_id = gateway_pool_id or new_solution_info["gateway_pool"]
                    compute_pool_id = compute_pool_id or new_solution_info["compute_pool"]
                    # deploy using the new information with a new uuid. a new uuid to not conflict with the old one when listing
                    solution_name = new_solution_info["name"]
                    backup_model = BACKUP_MODEL_FACTORY.get(f"{solution_name}_{owner}")
                    new_solution_uuid = uuid.uuid4().hex
                    metadata = {
                        "form_info": {"Solution name": solution_name, "chatflow": "threebot"},
                        "owner": f"{owner}.3bot",
                    }

                    # select node and update network
                    j.logger.debug(f"fetching network {new_solution_info['network']}")
                    network_view = deployer.get_network_view(
                        new_solution_info["network"], identity_name=identity.instance_name
                    )
                    j.logger.debug(f"searching for available node within pool {compute_pool_id}")
                    if node_id:
                        selected_node = zos._explorer.nodes.get(node_id)
                    else:
                        selected_node = deployer.schedule_container(
                            pool_id=compute_pool_id,
                            cru=new_solution_info["cpu"] + 1,
                            mru=(new_solution_info["memory"] / 1024) + 1,
                            sru=(new_solution_info["disk_size"] / 1024) + 0.25,
                            ip_version="IPv6",
                        )
                    j.logger.debug(f"found node with enough capacity {selected_node.node_id}")
                    j.logger.debug(f"adding node {selected_node.node_id} to network {network_view.name}")
                    result = deployer.add_network_node(
                        network_view.name,
                        selected_node,
                        compute_pool_id,
                        network_view,
                        bot=msg_bot,
                        identity_name=identity.instance_name,
                    )
                    if result:
                        for wid in result["ids"]:
                            success = deployer.wait_workload(
                                wid,
                                msg_bot,
                                breaking_node_id=selected_node.node_id,
                                identity_name=identity.instance_name,
                            )
                            if not success:
                                raise DeploymentFailed(
                                    f"Failed to add node {selected_node.node_id} to network {wid}", wid=wid
                                )
                        j.logger.debug(f"node {selected_node.node_id} added to network {network_view.name} successfuly")

                    j.logger.debug("searching for a free ip address")
                    network_view = network_view.copy()
                    ip_address = network_view.get_free_ip(selected_node)
                    j.logger.debug(f"found a free ip address {ip_address}")

                    workload_ids = []
                    j.logger.debug(f"fetching gateway {new_solution_info['gateway']}")
                    gateway = zos._explorer.gateway.get(new_solution_info["gateway"])
                    addresses = []
                    j.logger.debug(f"resolving gateway {gateway.node_id} name servers")
                    for ns in gateway.dns_nameserver:
                        try:
                            addresses.append(j.sals.nettools.get_host_by_name(ns))
                        except:
                            j.logger.error(f"failed to resolve name server {ns} of gateway {gateway.node_id}")
                    if not addresses:
                        raise StopChatFlow(
                            f"the gateway specfied {gateway.node_id} doesn't have any valid name servers"
                        )

                    domain = new_solution_info["domain"]
                    j.logger.debug(f"deploying domain {domain} pointing to addresses {addresses}")
                    workload_ids.append(
                        deployer.create_subdomain(
                            pool_id=gateway_pool_id,
                            gateway_id=gateway.node_id,
                            subdomain=domain,
                            addresses=addresses,
                            solution_uuid=new_solution_uuid,
                            identity_name=identity.instance_name,
                            **metadata,
                        )
                    )
                    j.logger.debug(f"waiting for domain workload {workload_ids[-1]} to deploy")
                    success = deployer.wait_workload(
                        workload_ids[-1], bot=msg_bot, identity_name=identity.instance_name
                    )
                    if not success:
                        raise DeploymentFailed(
                            f"Failed to create subdomain {domain} on gateway {gateway.node_id} {workload_ids[-1]}. The resources you paid for will be re-used in your upcoming deployments.",
                            wid=workload_ids[-1],
                            identity_name=identity.instance_name,
                        )

                    test_cert = j.config.get("TEST_CERT")
                    j.logger.debug("creating backup token")
                    backup_token = str(j.data.idgenerator.idgenerator.uuid.uuid4())
                    backup_model.token = backup_token
                    backup_model.tname = metadata["owner"]
                    backup_model.save()
                    j.logger.debug(f"backup token {backup_token} created for tname {backup_model.tname}")

                    environment_vars = {
                        "SDK_VERSION": new_solution_info["branch"],
                        "INSTANCE_NAME": new_solution_info["name"],
                        "THREEBOT_NAME": owner,
                        "DOMAIN": domain,
                        "SSHKEY": new_solution_info["public_key"],
                        "TEST_CERT": "true" if test_cert else "false",
                        "MARKETPLACE_URL": f"https://{j.sals.nginx.main.websites.threebot_deployer_threebot_deployer_root_proxy_443.domain}/",
                        "DEFAULT_IDENTITY": "test" if "test" in j.core.identity.me.explorer_url else "main",
                    }
                    j.logger.debug(f"deploying threebot container with environment {environment_vars}")

                    log_config = j.core.config.get("LOGGING_SINK", {})
                    if log_config:
                        log_config["channel_name"] = f'{owner}-{new_solution_info["name"]}'.lower()

                    workload_ids.append(
                        deployer.deploy_container(
                            pool_id=compute_pool_id,
                            node_id=selected_node.node_id,
                            network_name=network_view.name,
                            ip_address=ip_address,
                            flist=new_solution_info["flist"],
                            env=environment_vars,
                            cpu=new_solution_info["cpu"],
                            memory=new_solution_info["memory"],
                            disk_size=new_solution_info["disk_size"],
                            secret_env={"BACKUP_PASSWORD": backup_password, "BACKUP_TOKEN": backup_token},
                            interactive=False,
                            log_config=log_config,
                            solution_uuid=new_solution_uuid,
                            identity_name=identity.instance_name,
                            **metadata,
                        )
                    )
                    j.logger.debug(f"wating for threebot container workload {workload_ids[-1]} to be deployed")
                    success = deployer.wait_workload(
                        workload_ids[-1], bot=msg_bot, identity_name=identity.instance_name
                    )
                    if not success:
                        raise DeploymentFailed(
                            f"Failed to create container on node {selected_node.node_id} {workload_ids[-1]}. The resources you paid for will be re-used in your upcoming deployments.",
                            solution_uuid=new_solution_uuid,
                            wid=workload_ids[-1],
                            identity_name=identity.instance_name,
                        )
                    j.logger.debug(f"threebot container workload {workload_ids[-1]} deployed successfuly")

                    trc_log_config = j.core.config.get("LOGGING_SINK", {})
                    if trc_log_config:
                        trc_log_config["channel_name"] = f'{owner}-{new_solution_info["name"]}-trc'.lower()
                    identity_tid = identity.tid
                    secret = f"{identity_tid}:{uuid.uuid4().hex}"
                    j.logger.debug(f"deploying trc container")
                    workload_ids.extend(
                        deployer.expose_address(
                            pool_id=compute_pool_id,
                            gateway_id=gateway.node_id,
                            network_name=network_view.name,
                            local_ip=ip_address,
                            port=80,
                            tls_port=443,
                            trc_secret=secret,
                            node_id=selected_node.node_id,
                            reserve_proxy=True,
                            domain_name=domain,
                            proxy_pool_id=gateway_pool_id,
                            solution_uuid=new_solution_uuid,
                            log_config=trc_log_config,
                            identity_name=identity.instance_name,
                            **metadata,
                        )
                    )
                    j.logger.debug(f"wating for trc container workload {workload_ids[-1]} to be deployed")
                    success = deployer.wait_workload(
                        workload_ids[-1], bot=msg_bot, identity_name=identity.instance_name
                    )
                    if not success:
                        raise DeploymentFailed(
                            f"Failed to create TRC container on node {selected_node.node_id} {workload_ids[-1]}. The resources you paid for will be re-used in your upcoming deployments.",
                            solution_uuid=new_solution_uuid,
                            wid=workload_ids[-1],
                            identity_name=identity.instance_name,
                        )
                    j.logger.debug(f"trc container workload {workload_ids[-1]} deployed successfuly")

                    j.logger.debug(f"fetching farm information of pool {compute_pool_id}")
                    farm_id = deployer.get_pool_farm_id(compute_pool_id)
                    farm = zos._explorer.farms.get(farm_id)

                    j.logger.debug(f"saving new threebot local config with uuid {new_solution_uuid}")
                    instance_name = f"threebot_{new_solution_uuid}"
                    user_threebot = USER_THREEBOT_FACTORY.get(instance_name)
                    user_threebot.solution_uuid = new_solution_uuid
                    user_threebot.identity_tid = identity.tid
                    user_threebot.name = solution_name
                    user_threebot.owner_tname = threebot.owner_tname
                    user_threebot.farm_name = farm.name
                    user_threebot.state = ThreebotState.RUNNING
                    user_threebot.continent = farm.location.continent
                    user_threebot.explorer_url = identity.explorer_url
                    user_threebot.subdomain_wid = workload_ids[-4]
                    user_threebot.threebot_container_wid = workload_ids[-3]
                    user_threebot.trc_container_wid = workload_ids[-2]
                    user_threebot.reverse_proxy_wid = workload_ids[-1]
                    user_threebot.save()
                    j.logger.debug(f"threebot local config of uuid {new_solution_uuid} saved")
                    j.logger.debug(f"deleting old threebot local config with uuid {solution_uuid}")
                    USER_THREEBOT_FACTORY.delete(f"threebot_{solution_uuid}")
                    j.logger.debug("deployment successful")
                    return user_threebot
        except DeploymentFailed as e:
            retries -= 1
            if retries > 0:
                j.logger.error(f"3Bot {solution_uuid} redeployment failed. retrying {retries}")
                if bot and e.wid:
                    bot.md_show_update(f"Deployment Failed for wid {e.wid}. retrying {retries} ....")
