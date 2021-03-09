import math
import random
import uuid
from textwrap import dedent
import gevent

import requests

from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import StopChatFlow, chatflow_step
from jumpscale.sals.reservation_chatflow import DeploymentFailed, deployment_context
from jumpscale.sals.reservation_chatflow.deployer import GATEWAY_WORKLOAD_TYPES

from .chatflow import MarketPlaceChatflow
from .deployer import deployer
from .solutions import solutions
from jumpscale.clients.explorer.models import WorkloadType

FLAVORS = {"Silver": {"sru": 2}, "Gold": {"sru": 5}, "Platinum": {"sru": 10}}

RESOURCE_VALUE_KEYS = {"cru": "CPU {}", "mru": "Memory {} GB", "sru": "Disk {} GB [SSD]", "hru": "Disk {} GB [HDD]"}


class MarketPlaceAppsChatflow(MarketPlaceChatflow):
    def __init__(self, *args, **kwargs):
        self._branch = None
        super().__init__(*args, **kwargs)

    def _init_solution(self):
        self.md_show_update("It will take a few seconds to be ready to help you ...")
        # check stellar service
        if not j.clients.stellar.check_stellar_service():
            raise StopChatFlow("Payment service is currently down, try again later")
        self._validate_user()
        self.solution_id = uuid.uuid4().hex
        self.solution_metadata = {}
        self.username = self.user_info()["username"]
        self.solution_metadata["owner"] = self.username
        self.threebot_name = j.data.text.removesuffix(self.username, ".3bot")
        self.expiration = 60 * 60 * 3  # expiration 3 hours
        self.retries = 3
        self.custom_domain = False
        self.allow_custom_domain = False
        self.currency = "TFT"
        self.identity_name = j.core.identity.me.instance_name

    @property
    def branch(self):
        if not self._branch:
            try:
                path = j.packages.threebot_deployer.__file__
                git_client = j.clients.git.get("default_threebot")
                git_client.path = j.tools.git.find_git_path(path)
                git_client.save()
                self._branch = git_client.branch_name
            except Exception as e:
                # won't fail unless we move the 3bot deployer package
                j.logger.critical(
                    f"Using development as default branch. Threebot package location is changed/courrpted, Please fix me, Error: {str(e)}"
                )
                self._branch = "development"
        return self._branch

    def _choose_flavor(self, flavors=None):
        flavors = flavors or FLAVORS
        # use cru, mru, hru, mru values as defined in the class query if they are not specified in the flavor
        query = getattr(self, "query", {})
        for resource in query:
            for flavor_dict in flavors.values():
                if resource not in flavor_dict:
                    flavor_dict[resource] = query[resource]
        messages = []
        for flavor in flavors:
            flavor_specs = ""
            for key in flavors[flavor]:
                flavor_specs += f"{RESOURCE_VALUE_KEYS[key].format(flavors[flavor][key])} - "
            msg = f"{flavor} ({flavor_specs[:-3]})"
            messages.append(msg)
        chosen_flavor = self.single_choice(
            "Please choose the flavor you want to use (flavors define how much resources the deployed solution will use)",
            options=messages,
            required=True,
            default=messages[0],
        )
        self.flavor = chosen_flavor.split()[0]
        self.flavor_resources = flavors[self.flavor]

    def _select_farms(self):
        self.farm_name = random.choice(self.available_farms).name
        self.pool_farm_name = None

    def _select_pool_node(self):
        """Children should override this if they want to force the pool to contain a specific node id"""
        self.pool_node_id = None

    def _get_pool(self):
        self._get_available_farms(only_one=True)
        self._select_farms()
        self._select_pool_node()
        user_networks = solutions.list_network_solutions(self.solution_metadata["owner"])
        networks_names = [n["Name"] for n in user_networks]
        if "apps" in networks_names:
            # old user
            self.md_show_update("Checking for free resources .....")
            free_pools = deployer.get_free_pools(
                self.solution_metadata["owner"], farm_name=self.pool_farm_name, node_id=self.pool_node_id, **self.query
            )
            if free_pools:
                self.md_show_update(
                    "Searching for a best fit pool (best fit pool would try to find a pool that matches your resources or with least difference from the required specs)..."
                )
                # select free pool and extend if required
                pool, cu_diff, su_diff = deployer.get_best_fit_pool(
                    free_pools, self.expiration, farm_name=self.pool_farm_name, node_id=self.pool_node_id, **self.query
                )
                if cu_diff < 0 or su_diff < 0:
                    cu_diff = abs(cu_diff) if cu_diff < 0 else 0
                    su_diff = abs(su_diff) if su_diff < 0 else 0
                    pool_info = j.sals.zos.get().pools.extend(
                        pool.pool_id, math.ceil(cu_diff), math.ceil(su_diff), 0, currencies=[self.currency]
                    )
                    deployer.pay_for_pool(pool_info)
                    result = deployer.wait_pool_reservation(pool_info.reservation_id, bot=self)
                    if not result:
                        raise StopChatFlow(
                            f"can not provision resources. reservation_id: {pool_info.reservation_id}, pool_id: {pool.pool_id}"
                        )
                    self.pool_id = pool.pool_id
                else:
                    self.md_show_update(
                        f"Found a pool with enough capacity {pool.pool_id}. Deployment will continue in a moment..."
                    )
                    self.pool_id = pool.pool_id
            else:
                self.md_show_update("Reserving new resources....")
                self.pool_info = deployer.create_solution_pool(
                    bot=self,
                    username=self.solution_metadata["owner"],
                    farm_name=self.farm_name,
                    expiration=self.expiration,
                    currency=self.currency,
                    **self.query,
                )
                deployer.pay_for_pool(self.pool_info)
                result = deployer.wait_pool_reservation(self.pool_info.reservation_id, bot=self)
                if not result:
                    raise StopChatFlow(f"provisioning the pool timed out. pool_id: {self.pool_info.reservation_id}")
                self.pool_id = self.pool_info.reservation_id
        else:
            # new user
            self.pool_info = deployer.create_solution_pool(
                self,
                self.solution_metadata["owner"],
                self.farm_name,
                self.expiration,
                currency=self.currency,
                **self.query,
            )
            if self.pool_info.escrow_information.address.strip() == "":
                raise StopChatFlow(
                    f"provisioning the pool, invalid escrow information probably caused by a misconfigured, pool creation request was {self.pool_info}"
                )
            deployer.pay_for_pool(self.pool_info)
            result = deployer.wait_pool_reservation(self.pool_info.reservation_id, bot=self)
            if not result:
                raise StopChatFlow(f"provisioning the pool timed out. pool_id: {self.pool_info.reservation_id}")
            self.wgcfg = deployer.init_new_user_network(
                self, self.solution_metadata["owner"], self.pool_info.reservation_id
            )
            self.pool_id = self.pool_info.reservation_id

        self.network_view = deployer.get_network_view(
            f"{self.solution_metadata['owner']}_apps", identity_name=self.identity_name
        )
        return self.pool_id

    def _select_node(self):
        self.selected_node = deployer.schedule_container(self.pool_id, **self.query)

    @chatflow_step(title="New Expiration")
    def set_expiration(self):
        self.expiration = deployer.ask_expiration(self)

    @chatflow_step(title="SSH key (Optional)")
    def upload_public_key(self):
        self.public_key = (
            self.upload_file(
                "Please upload your public ssh key, this will allow you to access your threebot container using ssh"
            )
            or ""
        )
        self.public_key = self.public_key.strip()

    @chatflow_step(title="Backup credentials")
    def backup_credentials(self):
        form = self.new_form()
        aws_access_key_id = form.string_ask("AWS access key id", required=True)
        aws_secret_access_key = form.secret_ask("AWS secret access key", required=True)
        restic_password = form.secret_ask("Restic Password", required=True)
        restic_repository = form.string_ask(
            "Restic URL. Example: `s3backup.tfgw-testnet-01.gateway.tf`", required=True, md=True
        )
        form.ask("These credentials will be used to backup your solution.", md=True)
        self.aws_access_key_id = aws_access_key_id.value
        self.aws_secret_access_key = aws_secret_access_key.value
        self.restic_password = restic_password.value
        repo_name = self.solution_name.replace(".", "").replace("-", "")
        self.restic_repository = f"s3:{restic_repository.value}/{repo_name}"

    @deployment_context()
    def _deploy_network(self):
        # get ip address
        self.ip_address = None
        while not self.ip_address:
            self._select_node()
            result = deployer.add_network_node(
                self.network_view.name,
                self.selected_node,
                self.pool_id,
                self.network_view,
                bot=self,
                identity_name=self.identity_name,
                owner=self.solution_metadata.get("owner"),
            )
            if result:
                self.md_show_update("Deploying Network on Nodes....")
                for wid in result["ids"]:
                    success = deployer.wait_workload(wid, self, breaking_node_id=self.selected_node.node_id)
                    if not success:
                        raise DeploymentFailed(
                            f"Failed to add node {self.selected_node.node_id} to network {wid}. The resources you paid for will be re-used in your upcoming deployments.",
                            wid=wid,
                        )
                self.network_view = self.network_view.copy()
            self.ip_address = self.network_view.get_free_ip(self.selected_node)
        return self.ip_address

    def _get_custom_domain(self):
        self.md_show_update("Preparing gateways ...")
        gateways = deployer.list_all_gateways(self.username, self.farm_name)
        if not gateways:
            raise StopChatFlow(
                "There are no available gateways in the farms bound to your pools. The resources you paid for will be re-used in your upcoming deployments."
            )
        gateway_values = list(gateways.values())
        random.shuffle(gateway_values)
        self.addresses = []
        for gw_dict in gateway_values:
            gateway = gw_dict["gateway"]
            if not gateway.dns_nameserver:
                continue
            self.addresses = []
            for ns in gateway.dns_nameserver:
                try:
                    ip_address = j.sals.nettools.get_host_by_name(ns)
                except Exception as e:
                    j.logger.error(
                        f"failed to resolve nameserver {ns} of gateway {gateway.node_id} due to error {str(e)}"
                    )
                    continue
                self.addresses.append(ip_address)

            if self.addresses:
                self.gateway = gateway
                self.gateway_pool = gw_dict["pool"]
                self.domain = self.string_ask("Please specify the domain name you wish to bind to", required=True)
                self.domain = j.sals.zos.get().gateway.correct_domain(self.domain)
                res = """\
                ## Waiting for DNS Population...
                Please create an `A` record in your DNS manager for domain: `{{domain}}` pointing to:
                {% for ip in addresses -%}
                - {{ ip }}
                {% endfor %}
                """
                res = j.tools.jinja2.render_template(template_text=res, addresses=self.addresses, domain=self.domain)
                self.md_show_update(dedent(res), md=True)

                # wait for domain name to be created
                if not self.wait_domain(self.domain, self.addresses):
                    raise StopChatFlow(
                        "The specified domain name is not pointing to the gateway properly! Please bind it and try again. The resource you paid for will be re-used for your next deployment."
                    )
                return self.domain
        raise StopChatFlow("No available gateways. The resource you paid for will be re-used for your next deployment")

    def wait_domain(self, domain, ip_addresses=None, timeout=10):
        # preferably specify more than 5 minutes timeout for ttl changes
        end = j.data.time.now().timestamp + timeout * 60
        while j.data.time.now().timestamp < end:
            try:
                address = j.sals.nettools.get_host_by_name(domain)
                if ip_addresses:
                    if address in ip_addresses:
                        return True
                    continue
                else:
                    return True
            except Exception as e:
                j.logger.error(f"failed to resolve domain {domain} due to error {str(e)}")
                gevent.sleep(1)
        return False

    def _get_domain(self):
        # get domain for the ip address
        self.md_show_update("Preparing gateways ...")
        prefered_gw_farm = "csfarmer"
        gateways = deployer.list_all_gateways(self.username, prefered_gw_farm, identity_name=self.identity_name)
        if not gateways:
            raise StopChatFlow(
                "There are no available gateways in the farms bound to your pools. The resources you paid for will be re-used in your upcoming deployments."
            )

        domains = dict()
        is_managed_domains = False
        gateway_values = list(gateways.values())
        random.shuffle(gateway_values)
        blocked_domains = deployer.list_blocked_managed_domains()
        for gw_dict in gateway_values:
            gateway = gw_dict["gateway"]
            random.shuffle(gateway.managed_domains)
            for domain in gateway.managed_domains:
                self.addresses = []
                is_managed_domains = True
                if domain in blocked_domains or domain.startswith("vdc"):
                    continue

                # use 3bot with 3bot domains and solutions with webgw1 and webgw2
                if self.SOLUTION_TYPE == "threebot" and not domain.startswith("3bot"):
                    continue

                if self.SOLUTION_TYPE != "threebot" and not domain.startswith("webg"):
                    continue

                success = deployer.test_managed_domain(
                    gateway.node_id, domain, gw_dict["pool"].pool_id, gateway, identity_name=self.identity_name
                )
                if not success:
                    j.logger.warning(f"managed domain {domain} failed to populate subdomain. skipping")
                    deployer.block_managed_domain(domain)
                    continue
                else:
                    deployer.unblock_managed_domain(domain)
                domains[domain] = gw_dict
                self.gateway_pool = gw_dict["pool"]
                self.gateway = gw_dict["gateway"]
                managed_domain = domain

                solution_name = self.solution_name.replace(f"{self.solution_metadata['owner']}-", "").replace("_", "-")
                # check if domain name is free or append random number
                full_domain = f"{solution_name}.{managed_domain}"
                metafilter = lambda metadata: metadata.get("owner") == self.username
                # no need to load workloads in deployer object because it is already loaded when checking for name and/or network
                user_subdomains = {}
                all_domains = solutions._list_subdomain_workloads(
                    self.SOLUTION_TYPE, metadata_filters=[metafilter]
                ).values()
                for dom_list in all_domains:
                    for dom in dom_list:
                        user_subdomains[dom["domain"]] = dom

                while True:
                    if full_domain in user_subdomains:
                        # check if related container workloads still exist
                        dom = user_subdomains[full_domain]
                        sol_uuid = dom["uuid"]
                        if sol_uuid:
                            workloads = solutions.get_workloads_by_uuid(sol_uuid, "DEPLOY")
                            is_free = True
                            for w in workloads:
                                if w.info.workload_type == WorkloadType.Container:
                                    is_free = False
                                    break
                            if is_free:
                                solutions.cancel_solution_by_uuid(sol_uuid)
                                deployer.wait_workload_deletion(dom["wid"], timeout=3, identity_name=self.identity_name)

                    if j.tools.dnstool.is_free(full_domain):
                        self.domain = full_domain
                        break
                    else:
                        random_number = random.randint(1, 1000)
                        full_domain = f"{solution_name}-{random_number}.{managed_domain}"

                for ns in self.gateway.dns_nameserver:
                    try:
                        self.addresses.append(j.sals.nettools.get_host_by_name(ns))
                    except Exception as e:
                        j.logger.error(f"Failed to resolve DNS {ns}, this gateway will be skipped")
                if not self.addresses:
                    continue
                return self.domain
        if not is_managed_domains:
            raise StopChatFlow("Couldn't find managed domains in the available gateways. Please contact support.")
        else:
            raise StopChatFlow(
                "No active gateways were found.Please contact support. The resources you paid for will be re-used in your upcoming deployments."
            )

    def _config_logs(self):
        self.solution_log_config = j.core.config.get("LOGGING_SINK", {})
        if self.solution_log_config:
            self.solution_log_config[
                "channel_name"
            ] = f"{self.threebot_name}-{self.SOLUTION_TYPE}-{self.solution_name}".lower()
        self.nginx_log_config = j.core.config.get("LOGGING_SINK", {})
        if self.nginx_log_config:
            self.nginx_log_config[
                "channel_name"
            ] = f"{self.threebot_name}-{self.SOLUTION_TYPE}-{self.solution_name}-nginx".lower()
        self.trc_log_config = j.core.config.get("LOGGING_SINK", {})
        if self.trc_log_config:
            self.trc_log_config[
                "channel_name"
            ] = f"{self.threebot_name}-{self.SOLUTION_TYPE}-{self.solution_name}-trc".lower()

    @chatflow_step(title="Solution Name")
    def get_solution_name(self):
        self._init_solution()
        valid = False
        while not valid:
            self.solution_name = self.string_ask(
                "Please enter a name for your solution (will be used in listing and deletions in the future and in having a unique url)",
                required=True,
                is_identifier=True,
            )
            method = getattr(solutions, f"list_{self.SOLUTION_TYPE}_solutions")
            solutions_list = method(self.solution_metadata["owner"], sync=False)
            valid = True
            for sol in solutions_list:
                if sol["Name"] == self.solution_name:
                    valid = False
                    self.md_show("The specified solution name already exists. please choose another name.")
                    break
                valid = True
        self.solution_name = f"{self.solution_metadata['owner']}-{self.solution_name}"

    def _get_available_farms(self, only_one=True, identity_name=None):
        if getattr(self, "available_farms", None) is not None:
            return
        self.currency = getattr(self, "currency", "TFT")
        farm_message = f"""\
        Fetching available farms..
        """
        self.md_show_update(dedent(farm_message))

        self.available_farms = []
        farms = j.sals.zos.get(identity_name)._explorer.farms.list()
        # farm_names = ["freefarm"]  # DEUBGGING ONLY

        for farm in farms:
            available_ipv4, _, _, _, _ = deployer.check_farm_capacity(
                farm.name, currencies=[self.currency], ip_version="IPv4", **self.query
            )
            if available_ipv4:
                self.available_farms.append(farm)
                if only_one:
                    return
        if not self.available_farms:
            raise StopChatFlow("No available farms with enough resources for this deployment at the moment")

    @chatflow_step(title="Setup", disable_previous=True)
    def infrastructure_setup(self):
        self.md_show_update("Preparing Infrastructure...")
        self._get_pool()
        success = False
        while not success:
            try:
                self._deploy_network()
                success = True
            except DeploymentFailed as e:
                j.logger.error(e)
                if self.retries > 0:
                    self.md_show_update(f"Deployment failed on node {self.selected_node.node_id}. retrying....")
                    self.retries -= 1
                    self.ip_address = None
                    self._deploy_network()
                else:
                    raise e
        if self.allow_custom_domain:
            self.custom_domain = (
                self.single_choice(
                    "Do you want to manage the domain for the container or automatically get a domain of ours?",
                    ["Manage the Domain", "Automatically Get a Domain"],
                    default="Automatically Get a Domain",
                )
                == "Manage the Domain"
            )
        if self.custom_domain:
            self._get_custom_domain()
        else:
            self._get_domain()
        self._config_logs()

    @chatflow_step(title="Initializing", disable_previous=True)
    def initializing(self):
        self.md_show_update(f"Initializing your {self.SOLUTION_TYPE}...")

        if not j.sals.reservation_chatflow.wait_http_test(
            f"https://{self.domain}", timeout=600, verify=not j.config.get("TEST_CERT")
        ):
            stop_message = f"""\
                Failed to initialize {self.SOLUTION_TYPE}, please contact support with this information:
                Node: {self.selected_node.node_id},
                IP Address: {self.ip_address},
                Reservation ID: {self.resv_id},
                Pool ID: {self.pool_id},
                Domain: {self.domain}
                """
            self.stop(dedent(stop_message))

    # for threebot
    @chatflow_step(title="New Expiration")
    def new_expiration(self):
        DURATION_MAX = 9223372036854775807
        self.pool = j.sals.zos.get().pools.get(self.pool_id)
        if self.pool.empty_at < DURATION_MAX:
            # Pool currently being consumed (compute or storage), default is current pool empty at + 65 mins
            min_timestamp_fromnow = self.pool.empty_at - j.data.time.utcnow().timestamp
            default_time = self.pool.empty_at + 3900
        else:
            # Pool not being consumed (compute or storage), default is in 14 days (60*60*24*14 = 1209600)
            min_timestamp_fromnow = None
            default_time = j.data.time.utcnow().timestamp + 1209600
        self.expiration = deployer.ask_expiration(
            self, default_time, min=min_timestamp_fromnow, pool_empty_at=self.pool.empty_at
        )

    @chatflow_step(title="Payment")
    def solution_extension(self):
        self.md_show_update("Extending pool...")
        self.currencies = ["TFT"]

        self.pool_info, self.qr_code = deployer.extend_solution_pool(
            self, self.pool_id, self.expiration, self.currencies, **self.query
        )
        if self.pool_info and self.qr_code:
            # cru = 1 so cus will be = 0
            result = deployer.wait_pool_reservation(self.pool_info.reservation_id, qr_code=self.qr_code, bot=self)
            if not result:
                raise StopChatFlow(f"Waiting for pool payment timedout. pool_id: {self.pool_id}")

    @chatflow_step(title="Reservation", disable_previous=True)
    def reservation(self):
        identity_tid = j.core.identity.get(self.identity_name).tid
        self.secret = f"{identity_tid}:{uuid.uuid4().hex}"
        success = False
        while not success:
            try:
                self._deploy()
                success = True
            except DeploymentFailed as e:
                j.logger.error(e)
                self.retries -= 1
                if self.retries > 0:
                    self.md_show_update(
                        f"Deployment failed on node {self.selected_node.node_id}. retrying {self.retries}...."
                    )
                    gevent.sleep(3)
                    failed_workload = j.sals.zos.get().workloads.get(e.wid)
                    if failed_workload.info.workload_type in GATEWAY_WORKLOAD_TYPES:
                        self.addresses = []
                        if self.custom_domain:
                            self._get_custom_domain()
                        else:
                            self._get_domain()
                    else:
                        self.ip_address = None
                        self._deploy_network()
                else:
                    raise e

    @chatflow_step(title="Initializing backup")
    def init_backup(self):
        solution_name = self.solution_name.replace(".", "_").replace("-", "_")
        self.md_show_update("Setting container backup")
        SOLUTIONS_WATCHDOG_PATHS = j.sals.fs.join_paths(j.core.dirs.VARDIR, "solutions_watchdog")
        if not j.sals.fs.exists(SOLUTIONS_WATCHDOG_PATHS):
            j.sals.fs.mkdirs(SOLUTIONS_WATCHDOG_PATHS)

        restic_instance = j.tools.restic.get(solution_name)
        restic_instance.password = self.restic_password
        restic_instance.repo = self.restic_repository
        restic_instance.extra_env = {
            "AWS_ACCESS_KEY_ID": self.aws_access_key_id,
            "AWS_SECRET_ACCESS_KEY": self.aws_secret_access_key,
        }
        restic_instance.save()
        try:
            restic_instance.init_repo()
        except Exception as e:
            j.tools.restic.delete(solution_name)
            raise j.exceptions.Input(f"Error: Failed to reach repo {self.restic_repository} due to {str(e)}")
        restic_instance.start_watch_backup(SOLUTIONS_WATCHDOG_PATHS)

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        display_name = self.solution_name.replace(f"{self.solution_metadata['owner']}-", "")
        message = f"""\
        # You deployed a new instance {display_name} of {self.SOLUTION_TYPE}
        <br />\n
        - You can access it via the browser using: <a href="https://{self.domain}" target="_blank">https://{self.domain}</a>
        """
        self.md_show(dedent(message), md=True)
