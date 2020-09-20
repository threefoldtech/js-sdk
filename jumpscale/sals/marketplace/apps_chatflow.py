import math
import random
import uuid
from textwrap import dedent

import requests

from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import StopChatFlow, chatflow_step
from jumpscale.sals.reservation_chatflow import DeploymentFailed, deployment_context

from .chatflow import MarketPlaceChatflow
from .deployer import deployer
from .solutions import solutions

FLAVORS = {
    "Silver": {"sru": 2,},
    "Gold": {"sru": 5,},
    "Platinum": {"sru": 10,},
}

RESOURCE_VALUE_KEYS = {
    "cru": "CPU {}",
    "mru": "Memory {} GB",
    "sru": "Disk {} GB [SSD]",
    "hru": "Disk {} GB [HDD]",
}


class MarketPlaceAppsChatflow(MarketPlaceChatflow):
    def _init_solution(self):
        self.md_show_update("Checking payment service...")
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
            "Please choose the flavor you want ot use (flavors define how much resources the deployed solution will use)",
            options=messages,
            required=True,
            default=messages[0],
        )
        self.flavor = chosen_flavor.split()[0]
        self.flavor_resources = flavors[self.flavor]

    def _get_pool(self):
        self.currency = "TFT"
        available_farms = []
        farm_names = ["freefarm"]  # [f.name for f in j.sals.zos._explorer.farms.list()]  # TODO: RESTORE LATER

        for farm_name in farm_names:
            available, _, _, _, _ = deployer.check_farm_capacity(farm_name, currencies=[self.currency], **self.query)
            if available:
                available_farms.append(farm_name)

        self.farm_name = random.choice(available_farms)

        user_networks = solutions.list_network_solutions(self.solution_metadata["owner"])
        networks_names = [n["Name"] for n in user_networks]
        if "apps" in networks_names:
            # old user
            self.md_show_update("Checking for free resources .....")
            free_pools = deployer.get_free_pools(self.solution_metadata["owner"])
            if free_pools:
                self.md_show_update(
                    "Searching for a best fit pool (best fit pool would try to find a pool that matches your resources or with least difference from the required specs)..."
                )
                # select free pool and extend if required
                pool, cu_diff, su_diff = deployer.get_best_fit_pool(
                    free_pools, self.expiration, free_to_use=self.currency == "FreeTFT", **self.query
                )
                if cu_diff < 0 or su_diff < 0:
                    cu_diff = abs(cu_diff) if cu_diff < 0 else 0
                    su_diff = abs(su_diff) if su_diff < 0 else 0
                    pool_info = j.sals.zos.pools.extend(
                        pool.pool_id, math.ceil(cu_diff), math.ceil(su_diff), currencies=[self.currency]
                    )
                    deployer.pay_for_pool(pool_info)
                    trigger_cus = pool.cus + (cu_diff * 0.9) if cu_diff else 0
                    trigger_sus = pool.sus + (su_diff * 0.9) if su_diff else 0
                    result = deployer.wait_demo_payment(
                        self, pool.pool_id, trigger_cus=trigger_cus, trigger_sus=trigger_sus
                    )
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
                result = deployer.wait_demo_payment(self, self.pool_info.reservation_id)
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
            deployer.pay_for_pool(self.pool_info)
            result = deployer.wait_demo_payment(self, self.pool_info.reservation_id)
            if not result:
                raise StopChatFlow(f"provisioning the pool timed out. pool_id: {self.pool_info.reservation_id}")
            deployer.init_new_user_network(self, self.solution_metadata["owner"], self.pool_info.reservation_id)
            self.pool_id = self.pool_info.reservation_id

        return self.pool_id

    @deployment_context()
    def _deploy_network(self):
        # get ip address
        self.network_view = deployer.get_network_view(f"{self.solution_metadata['owner']}_apps")
        self.ip_address = None
        while not self.ip_address:
            self.selected_node = deployer.schedule_container(self.pool_id, **self.query)
            result = deployer.add_network_node(
                self.network_view.name,
                self.selected_node,
                self.pool_id,
                self.network_view,
                bot=self,
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

    def _get_domain(self):
        # get domain for the ip address
        self.md_show_update("Preparing gateways ...")
        gateways = deployer.list_all_gateways(self.username)
        if not gateways:
            raise StopChatFlow(
                "There are no available gateways in the farms bound to your pools. The resources you paid for will be re-used in your upcoming deployments."
            )

        domains = dict()
        is_http_failure = False
        is_managed_domains = False
        for gw_dict in gateways.values():
            gateway = gw_dict["gateway"]
            for domain in gateway.managed_domains:
                is_managed_domains = True
                try:
                    if j.sals.crtsh.has_reached_limit(domain):
                        continue
                except requests.exceptions.HTTPError:
                    is_http_failure = True
                    continue
                domains[domain] = gw_dict

        if not domains:
            if is_http_failure:
                raise StopChatFlow(
                    'An error encountered while trying to fetch certifcates information from <a href="crt.sh" target="_blank">crt.sh</a>. Please try again later.'
                )
            elif not is_managed_domains:
                raise StopChatFlow("Couldn't find managed domains in the available gateways. Please contact support.")
            else:
                raise StopChatFlow(
                    "Letsencrypt limit has been reached on all gateways. The resources you paid for will be re-used in your upcoming deployments."
                )

        self.domain = random.choice(list(domains.keys()))

        self.gateway = domains[self.domain]["gateway"]
        self.gateway_pool = domains[self.domain]["pool"]

        solution_name = self.solution_name.replace(f"{self.solution_metadata['owner']}-", "").replace("_", "-")
        owner_prefix = self.solution_metadata["owner"].replace(".3bot", "").replace(".", "").replace("_", "-")
        solution_type = self.SOLUTION_TYPE.replace(".", "").replace("_", "-")
        # check if domain name is free or append random number
        full_domain = f"{owner_prefix}-{solution_type}-{solution_name}.{self.domain}"
        while True:
            if j.tools.dnstool.is_free(full_domain):
                self.domain = full_domain
                break
            else:
                random_number = random.randint(1000, 100000)
                full_domain = f"{owner_prefix}-{solution_type}-{solution_name}-{random_number}.{self.domain}"

        self.addresses = []
        for ns in self.gateway.dns_nameserver:
            self.addresses.append(j.sals.nettools.get_host_by_name(ns))

        self.secret = f"{j.core.identity.me.tid}:{uuid.uuid4().hex}"
        return self.domain

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

    @chatflow_step(title="Setup", disable_previous=True)
    def infrastructure_setup(self):
        self.md_show_update("Preparing Infrastructure...")
        self._get_pool()
        self._deploy_network()
        self._get_domain()

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
        self.pool = j.sals.zos.pools.get(self.pool_id)
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
        self.currencies = ["TFT"]
        self.pool_info, self.qr_code = deployer.extend_solution_pool(
            self, self.pool_id, self.expiration, self.currencies, **self.query
        )
        if self.pool_info and self.qr_code:
            # cru = 1 so cus will be = 0
            result = deployer.wait_pool_payment(self, self.pool_id, qr_code=self.qr_code, trigger_sus=self.pool.sus + 1)
            if not result:
                raise StopChatFlow(f"Waiting for pool payment timedout. pool_id: {self.pool_id}")

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        display_name = self.solution_name.replace(f"{self.solution_metadata['owner']}-", "")
        message = f"""\
        # You deployed a new instance {display_name} of {self.SOLUTION_TYPE}
        <br />\n
        - You can access it via the browser using: <a href="https://{self.domain}" target="_blank">https://{self.domain}</a>
        """
        self.md_show(dedent(message), md=True)
