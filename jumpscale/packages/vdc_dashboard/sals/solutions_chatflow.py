import random
import gevent
import requests
import uuid
import os
from textwrap import dedent
from time import time

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
PREFERRED_FARM = "csfarmer"
POD_INITIALIZING_TIMEOUT = 120


class SolutionsChatflowDeploy(GedisChatBot):
    def _init_solution(self):
        # TODO: te be removed
        self.user_info_data = self.user_info()
        self.username = os.environ.get("VDC_OWNER_TNAME") or j.core.identity.me.tname
        self.solution_id = uuid.uuid4().hex
        self.ip_version = "IPv6"
        self.chart_config = {}

    def _get_kube_config(self):
        if j.sals.vdc.list_all():
            self.vdc_name = list(j.sals.vdc.list_all())[0]
        else:
            raise StopChatFlow(f"No Virtual Data Centres(VDC) were found.", htmlAlert=True)
        self.vdc_info = {}
        self.vdc = j.sals.vdc.find(name=self.vdc_name, owner_tname=self.username, load_info=True)
        self.identity_name = j.core.identity.me.instance_name
        self.secret = f"{self.vdc.identity_tid}:{uuid.uuid4().hex}"
        for node in self.vdc.kubernetes:
            if node.role == KubernetesRole.MASTER:
                self.vdc_info["master_ip"] = node.ip_address
                self.vdc_info["pool_id"] = node.pool_id
                self.vdc_info["public_ip"] = node.public_ip
                self.vdc_info["farm_name"] = j.core.identity.me.explorer.farms.get(
                    j.core.identity.me.explorer.nodes.get(node.node_id).farm_id
                ).name
                self.vdc_info["kube_config_path"] = "/root/.kube/config"
                self.vdc_info["network_name"] = self.vdc_name
                self.vdc_info["network_view"] = deployer.get_network_view(
                    self.vdc_name, identity_name=self.identity_name
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
        memory = int(self.resources_limits["memory"][:-2])
        cpu = int(self.resources_limits["cpu"][:-1])
        monitor = self.vdc.get_kubernetes_monitor()
        if not monitor.has_enough_resources(cpu=cpu, memory=memory):
            wids = monitor.extend(bot=self)
            if not wids:
                raise StopChatFlow(
                    f"There are not enough resources to deploy cpu: {cpu}, memory: {memory}. current cluster resources: {monitor.node_stats}"
                )

    def _configure_admin_username_password(self):
        form = self.new_form()
        admin_user_message = "Admin username"
        admin_pass_message = "Admin Password (should be at least 10 characters long)"
        admin_username = form.string_ask(admin_user_message, required=True, is_identifier=True)
        admin_password = form.secret_ask(admin_pass_message, required=True, is_identifier=True, min_length=10)
        form.ask()
        self.admin_username = admin_username.value
        self.admin_password = admin_password.value

    def _ask_smtp_settings(self):
        form = self.new_form()
        smtp_host = form.string_ask("SMTP Host", required=True)
        smtp_port = form.string_ask("SMTP Port", required=True)
        smtp_username = form.string_ask("SMTP Username", required=True)
        smtp_password = form.secret_ask("SMTP Password", required=True)
        form.ask()
        self.smtp_host = smtp_host.value
        self.smtp_port = f'"{smtp_port.value}"'
        self.smtp_username = smtp_username.value
        self.smtp_password = smtp_password.value

    def _get_domain(self):
        # get domain for the ip address
        self.md_show_update("Preparing gateways ...")
        self.preferred_farm_gw = True
        gateways = {}

        # try preferred farm gateways first
        gateways = deployer.list_all_gateways(self.username, PREFERRED_FARM, identity_name=self.identity_name)
        if not gateways:
            self.preferred_farm_gw = False
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
                # vdc 3bot to be vdctest.grid.tf, solutions to be webg1test.grid.tf or alike
                if domain.startswith("vdc") or domain.startswith("3bot"):
                    continue
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

                if self.domain_type == "Choose a custom subdomain on a gateway":
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
                        if self.domain_type == "Choose a custom subdomain on a gateway":
                            self.custom_subdomain = self.string_ask(
                                f"Please enter another subdomain as {self.custom_subdomain} is unavailable on {managed_domain}",
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
                "No active gateways were found.Please contact support. The resources you paid for will be re-used in your upcoming deployments."
            )

    def _get_custom_domain(self):
        valid = False
        cluster_ip = self.vdc_info["public_ip"]
        while not valid:
            custom_domain = self.string_ask(
                f"Please enter the domain name, make sure the domain points to {cluster_ip}.", required=True,
            )
            if j.sals.nettools.get_host_by_name(custom_domain) != cluster_ip:
                self.md_show(f"The domain {custom_domain} doesn't point to {cluster_ip}.")
            else:
                valid = True
                self.domain = custom_domain

    @deployment_context()
    def _create_subdomain(self):
        self.workload_ids = []
        metadata = {
            "name": self.release_name,
            "form_info": {"chatflow": self.SOLUTION_TYPE, "Solution name": self.release_name},
        }
        self.workload_ids.append(
            deployer.create_subdomain(
                pool_id=self.gateway_pool.pool_id,
                gateway_id=self.gateway.node_id,
                subdomain=self.domain,
                addresses=[self.vdc_info["public_ip"]],
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

    def _get_vdc_info(self):
        self.md_show_update("Preparing the chatflow...")
        self._init_solution()
        self._get_kube_config()
        self.k8s_client = j.sals.kubernetes.Manager(config_path=self.vdc_info["kube_config_path"])

    @chatflow_step(title="Solution Name")
    def get_release_name(self):
        self._get_vdc_info()
        message = "Please enter a name for your solution (will be used in listing and deletions in the future and in having a unique url)"
        releases = [release["name"] for release in self.k8s_client.list_deployed_releases()]
        self.release_name = self.string_ask(
            message, required=True, is_identifier=True, not_exist=["solution name", releases], md=True
        )

    @chatflow_step(title="Create subdomain")
    def create_subdomain(self):
        choices = [
            "Choose subdomain for me on a gateway",
            "Choose a custom subdomain on a gateway",
            "Choose a custom domain",
        ]
        self.domain_type = self.single_choice(
            "Select the domain type", choices, default="Choose subdomain for me on a gateway"
        )
        # get self.domain
        if self.domain_type == "Choose a custom domain":
            self._get_custom_domain()
        else:
            self._get_domain()
        self._create_subdomain()

        # subdomain selected on gateway on preferred farm
        if self.preferred_farm_gw:
            self.chart_config.update({"global.ingress.certresolver": "gridca"})

    @chatflow_step(title="Installation")
    def install_chart(self):
        try:
            helm_repos_urls = [repo["url"] for repo in self.k8s_client.list_helm_repos()]
        except Exception as e:
            j.logger.warning(f"The following error happened with helm:\n {str(e)}")  # TODO: tweak this
            helm_repos_urls = []
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

    def chart_pods_started(self):
        pods_status_info = self.k8s_client.execute_native_cmd(
            cmd=f"kubectl get pods -l app.kubernetes.io/name={self.SOLUTION_TYPE} -l app.kubernetes.io/instance={self.release_name} -o=jsonpath='{{.items[*].status.phase}}'"
        )
        if "Pending" in pods_status_info:
            return False
        return True

    def _has_domain(self):
        return getattr(self, "domain", None) is not None

    def chart_resource_failure(self):
        pods_info = self.k8s_client.execute_native_cmd(
            cmd=f"kubectl get pods -l app.kubernetes.io/name={self.SOLUTION_TYPE} -l app.kubernetes.io/instance={self.release_name} -o=jsonpath='{{.items[*].status.conditions[*].message}}'"
        )  # Gets the last event message
        if "Insufficient" in pods_info:
            return True
        return False

    @chatflow_step(title="Initializing", disable_previous=True)
    def initializing(self, timeout=300):
        self.md_show_update(f"Initializing your {self.SOLUTION_TYPE}...")
        domain_message = ""
        if self._has_domain():
            domain_message = f"Domain: {self.domain}"
        error_message_template = f"""\
                Failed to initialize {self.SOLUTION_TYPE}, please contact support with this information:

                {domain_message}
                VDC Name: {self.vdc_name}
                Farm name: {self.vdc_info["farm_name"]}
                Reason: {{reason}}
                """
        start_time = time()
        while time() - start_time <= POD_INITIALIZING_TIMEOUT:
            if self.chart_pods_started():
                break
            gevent.sleep(1)

        if not self.chart_pods_started() and self.chart_resource_failure():
            stop_message = error_message_template.format(
                reason="Couldn't find resources in the cluster for the solution"
            )
            self.k8s_client.delete_deployed_release(self.release_name)
            self.stop(dedent(stop_message))

        if self._has_domain() and not j.sals.reservation_chatflow.wait_http_test(
            f"https://{self.domain}", timeout=timeout - POD_INITIALIZING_TIMEOUT, verify=False
        ):
            stop_message = error_message_template.format(reason="Couldn't reach the website after deployment")
            self.stop(dedent(stop_message))

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self, extra_info=""):
        domain_message = ""
        if self._has_domain():
            domain_message = f'- You can access it via the browser using: <a href="https://{self.domain}" target="_blank">https://{self.domain}</a><br />\n'
        message = f"""\
        # You deployed a new instance {self.release_name} of {self.SOLUTION_TYPE}
        <br />\n
        {domain_message}
        {extra_info}
        """
        self.md_show(dedent(message), md=True)
