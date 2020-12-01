import random
import requests
import uuid
from textwrap import dedent

from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.reservation_chatflow import deployment_context, DeploymentFailed
from jumpscale.sals.marketplace import deployer, solutions
from jumpscale.clients.explorer.models import WorkloadType
from jumpscale.sals.vdc.models import KubernetesRole

CHART_LIMITS = {
    "Silver": {"cpu": "1000m", "memory": "1024Mi"},
    "Gold": {"cpu": "2000m", "memory": "2048Mi"},
    "Platinum": {"cpu": "4000m", "memory": "4096Mi"},
}
RESOURCE_VALUE_TEMPLATE = {"cpu": "CPU {}", "memory": "Memory {}"}
HELM_REPOS = {"marketplace": {"name": "marketplace", "url": "https://threefoldtech.github.io/vdc-solutions-charts/"}}
VDC_ENDPOINT = "/vdc"


class SolutionsChatflowDeploy(GedisChatBot):
    def _init_solution(self):
        self.user_info_data = self.user_info()
        self.username = self.user_info_data["username"]
        self.solution_id = uuid.uuid4().hex
        self.ip_version = "IPv6"
        self.chart_config = {}

    def _get_kube_config(self):
        vdc_names = [vdc.vdc_name for vdc in j.sals.vdc.list(self.username)]
        if not vdc_names:
            raise StopChatFlow(
                f'No Virtual Data Centres(VDC) were found. To deploy one please head to your <a href="{VDC_ENDPOINT}" target="_blank">VDC deployer</a>',
                htmlAlert=True,
            )
        vdc_selected = self.single_choice(
            f"Choose the vdc to install {self.SOLUTION_TYPE} on", options=vdc_names, required=True
        )
        self.vdc_info = {}
        self.vdc = j.sals.vdc.find(vdc_name=vdc_selected, owner_tname=self.username, load_info=True)
        self.identity_name = f"vdc_ident_{self.vdc.solution_uuid}"
        self.secret = f"{self.vdc.identity_tid}:{uuid.uuid4().hex}"
        for node in self.vdc.kubernetes:
            if node.role == KubernetesRole.MASTER:
                self.vdc_info["master_ip"] = node.ip_address
                self.vdc_info["pool_id"] = node.pool_id
                self.vdc_info["public_ip"] = node.public_ip
                self.vdc_info["farm_name"] = j.core.identity.me.explorer.farms.get(
                    j.core.identity.me.explorer.nodes.get(node.node_id).farm_id
                ).name
                self.vdc_info[
                    "kube_config_path"
                ] = f"{j.core.dirs.CFGDIR}/vdc/kube/{self.username.rstrip('.3bot')}/{vdc_selected}.yaml"
                self.vdc_info["network_name"] = vdc_selected
                self.vdc_info["network_view"] = deployer.get_network_view(
                    vdc_selected, identity_name=self.identity_name
                )
                break

    def _choose_flavor(self, chart_limits=None):
        chart_limits = chart_limits or CHART_LIMITS
        messages = []
        for flavor in chart_limits:
            flavor_specs = ""
            for key in chart_limits[flavor]:
                flavor_specs += f"{RESOURCE_VALUE_TEMPLATE[key].format(chart_limits[flavor][key])} - "
            msg = f"{flavor} ({flavor_specs[:-3]})"
            messages.append(msg)
        chosen_flavor = self.single_choice(
            "Please choose the flavor you want to use (helm chart limits define how much resources the deployed solution will use)",
            options=messages,
            required=True,
            default=messages[0],
        )
        flavor = chosen_flavor.split()[0]
        self.resources_limits = chart_limits[flavor]

    def _get_domain(self):
        # get domain for the ip address
        self.md_show_update("Preparing gateways ...")
        gateways = deployer.list_all_gateways(
            self.username, self.vdc_info["farm_name"], identity_name=self.identity_name
        )
        if not gateways:
            raise StopChatFlow(
                "There are no available gateways in the farms bound to your pools. The resources you paid for will be re-used in your upcoming deployments."
            )

        domains = dict()
        is_http_failure = False
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
                if domain in blocked_domains:
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
                try:
                    if j.sals.crtsh.has_reached_limit(domain):
                        continue
                except requests.exceptions.HTTPError:
                    is_http_failure = True
                    continue
                domains[domain] = gw_dict
                self.gateway_pool = gw_dict["pool"]
                self.gateway = gw_dict["gateway"]
                managed_domain = domain

                release_name = self.release_name.replace("_", "-")
                owner_prefix = self.username.replace(".3bot", "").replace(".", "").replace("_", "-")
                solution_type = self.SOLUTION_TYPE.replace(".", "").replace("_", "-")
                # check if domain name is free or append random number

                if self.domain_type == "Custom domain":
                    self.custom_subdomain = self.string_ask(
                        f"Please enter a subdomain to be added to {managed_domain}", required=True, is_identifier=True
                    )
                    full_domain = f"{self.custom_subdomain}.{managed_domain}"
                else:
                    full_domain = f"{owner_prefix}-{solution_type}-{release_name}.{managed_domain}"

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

                    if j.tools.dnstool.is_free(full_domain):
                        self.domain = full_domain
                        break
                    else:
                        if self.domain_type == "Custom domain":
                            self.custom_subdomain = self.string_ask(
                                f"Please enter anthor subdomain as {self.custom_subdomain} is unavilable on {managed_domain}",
                                required=True,
                                is_identifier=True,
                            )
                            full_domain = f"{self.custom_subdomain}.{managed_domain}"
                        else:
                            random_number = random.randint(1000, 100000)
                            full_domain = (
                                f"{owner_prefix}-{solution_type}-{release_name}-{random_number}.{managed_domain}"
                            )

                for ns in self.gateway.dns_nameserver:
                    try:
                        self.addresses.append(j.sals.nettools.get_host_by_name(ns))
                    except Exception as e:
                        j.logger.error(f"Failed to resolve DNS {ns}, this gateway will be skipped")
                if not self.addresses:
                    continue
                return self.domain

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

    @deployment_context()
    def _deploy(self):
        self.workload_ids = []
        metadata = {
            "name": self.release_name,
            "form_info": {"chatflow": self.SOLUTION_TYPE, "Solution name": self.release_name},
        }
        # TODO: get node related to vdc
        selected_node = deployer.schedule_container(self.vdc_info["pool_id"], ip_version=self.ip_version)
        # TODO: Do we need logs?
        self.nginx_log_config = j.core.config.get("LOGGING_SINK", {})
        if self.nginx_log_config:
            self.nginx_log_config[
                "channel_name"
            ] = f"{self.username}-{self.SOLUTION_TYPE}-{self.release_name}-nginx".lower()
        # reserve subdomain
        self.workload_ids.append(
            deployer.create_subdomain(
                pool_id=self.gateway_pool.pool_id,
                gateway_id=self.gateway.node_id,
                subdomain=self.domain,
                addresses=self.addresses,
                solution_uuid=self.solution_id,
                identity_name=self.identity_name,
                **metadata,
            )
        )
        success = deployer.wait_workload(self.workload_ids[0], self)
        if not success:
            raise DeploymentFailed(
                f"Failed to create subdomain {self.domain} on gateway {self.gateway.node_id} {self.workload_ids[0]}. The resources you paid for will be re-used in your upcoming deployments.",
                wid=self.workload_ids[0],
            )

        # expose solution on nginx container
        _id, _ = deployer.expose_and_create_certificate(
            pool_id=self.vdc_info["pool_id"],
            gateway_id=self.gateway.node_id,
            network_name=self.vdc_info["network_view"].name,
            trc_secret=self.secret,
            domain=self.domain,
            email=self.user_info_data["email"],
            solution_ip=self.vdc_info["master_ip"],
            solution_port=80,
            enforce_https=False,
            proxy_pool_id=self.gateway_pool.pool_id,
            node_id=selected_node.node_id,
            solution_uuid=self.solution_id,
            log_config=self.nginx_log_config,
            identity_name=self.identity_name,
            **metadata,
        )
        self.workload_ids.append(_id)
        success = deployer.wait_workload(_id, self)
        if not success:
            # solutions.cancel_solution(self.workload_ids)
            raise DeploymentFailed(
                f"Failed to create TRC container on node {selected_node.node_id}"
                f" {_id}. The resources you paid for will be re-used in your upcoming deployments.",
                solution_uuid=self.solution_id,
                wid=self.workload_ids[-1],
            )

    @chatflow_step(title="VDC selection")
    def select_vdc(self):
        self.md_show_update("Preparing the chatflow...")
        self._init_solution()
        self._get_kube_config()
        self.k8s_client = j.sals.kubernetes.Manager(config_path=self.vdc_info["kube_config_path"])

    @chatflow_step(title="Solution Name")
    def get_release_name(self):
        message = "Please enter a name for your solution (will be used in listing and deletions in the future and in having a unique url)"
        while True:
            self.release_name = self.string_ask(message, required=True, is_identifier=True, md=True)
            # TODO: Check if solution name exist
            releases = [release["name"] for release in self.k8s_client.list_deployed_releases()]
            if not self.release_name in releases:
                break
            message = "Release name already exists.</br>Please enter a name for your solution (will be used in listing and deletions in the future and in having a unique url)"

    @chatflow_step(title="Create subdomain")
    def create_subdomain(self):
        choices = ["Create standard Subdomain", "Custom domain"]
        self.domain_type = self.single_choice("Select the domain type", choices, default="Create standard Domain")
        # get self.domain
        self._get_domain()
        self._deploy()

    @chatflow_step(title="Installation")
    def install_chart(self):
        helm_repos_urls = [repo["url"] for repo in self.k8s_client.list_helm_repo()]
        if HELM_REPOS[self.HELM_REPO_NAME]["url"] not in helm_repos_urls:
            self.k8s_client.add_helm_repo(
                HELM_REPOS[self.HELM_REPO_NAME]["name"], HELM_REPOS[self.HELM_REPO_NAME]["url"]
            )
        self.k8s_client.update_repos()
        self.chart_config.update({"solution_uuid": self.solution_id})
        self.k8s_client.install_chart(
            release=self.release_name,
            chart_name=f"{self.HELM_REPO_NAME}/{self.SOLUTION_TYPE}",
            extra_config=self.chart_config,
        )

    @chatflow_step(title="Initializing", disable_previous=True)
    def initializing(self):
        public_ip = self.vdc_info["public_ip"]
        self.md_show_update(f"Initializing your {self.SOLUTION_TYPE}...")

        if not j.sals.reservation_chatflow.wait_http_test(
            f"https://{public_ip}", timeout=300, verify=not j.config.get("TEST_CERT")
        ):
            stop_message = f"""\
                Failed to initialize {self.SOLUTION_TYPE}, please contact support with this information:

                Domain: {public_ip}
                VDC Name: {self.vdc.vdc_name}
                Farm name: {self.vdc_info["farm_name"]}
                """
            self.stop(dedent(stop_message))

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        message = f"""\
        # You deployed a new instance {self.release_name} of {self.SOLUTION_TYPE}
        <br />\n
        - You can access it via the browser using: <a href="https://{public_ip}" target="_blank">https://{public_ip}</a>
        """
        self.md_show(dedent(message), md=True)
