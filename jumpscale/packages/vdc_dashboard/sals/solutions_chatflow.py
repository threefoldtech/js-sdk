import random
import gevent
import requests
import uuid
import nacl
from textwrap import dedent
from time import time

from jumpscale.loader import j
from jumpscale.core.base import Base, fields
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
HELM_REPOS = {
    "marketplace": {"name": "marketplace", "url": "https://threefoldtech.github.io/vdc-solutions-charts/"}
}  # TODO: revert to threefoldtech
VDC_ENDPOINT = "/vdc"
PREFERRED_FARM = "csfarmer"
POD_INITIALIZING_TIMEOUT = 600


class ChartConfig(Base):
    cert_resolver = fields.String(default="le")
    domain = fields.String(default=None)
    domain_type = fields.String()
    resources_limits = fields.Typed(dict, default={})
    backup = fields.String(default="vdc")
    ip_version = fields.String(default="IPv6")
    extra_config = fields.Typed(dict, default={})


class DeploymentConfig(Base):
    username = fields.String()
    release_name = fields.String()
    chart_config = fields.Object(ChartConfig)


class SolutionsChatflowDeploy(GedisChatBot):
    CHART_NAME = None
    ADDITIONAL_QUERIES = None  # list of {"cpu": x(m), "memory": x(Mi)} used by chart dependencies
    alert_view_url = "/vdc_dashboard/#/alerts"

    @property
    def chart_name(self):
        return self.CHART_NAME or self.SOLUTION_TYPE

    def get_config(self):
        return {}  # to be overridden in the chart chatflow

    def get_config_string_safe(self):
        """ Get config that we want to ensure to be set as
         string during passing the values to helm chart example passwords, ports,.... etc.
         to prevent helm from doing wrong type casting

        Returns:
            dict: configurations to be passed to helm

        """
        return {}  # to be overridden in the chart chatflow

    def _init_solution(self):
        user_info_data = self.user_info()
        self.config = DeploymentConfig()
        self.config.username = user_info_data["username"]
        self.solution_id = uuid.uuid4().hex

    def _get_kube_config(self):
        if j.sals.vdc.list_all():
            self.vdc_name = list(j.sals.vdc.list_all())[0]
        else:
            raise StopChatFlow(f"No Virtual Data Centers(VDC) were found.", htmlAlert=True)
        self.vdc_info = {}
        self.vdc = j.sals.vdc.find(name=self.vdc_name, load_info=True)
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
                self.vdc_info["kube_config_path"] = j.sals.fs.expanduser("~/.kube/config")
                self.vdc_info["network_name"] = self.vdc_name
                self.vdc_info["network_view"] = deployer.get_network_view(
                    self.vdc_name, identity_name=self.identity_name
                )
                break

    def _validate_resource_limits(self, cpu, memory, no_nodes=1):
        queries = [{"cpu": cpu, "memory": memory}] * no_nodes
        if self.ADDITIONAL_QUERIES:
            queries += self.ADDITIONAL_QUERIES
        monitor = self.vdc.get_kubernetes_monitor()
        if not monitor.check_deployment_resources(queries):
            wids = monitor.extend(bot=self)
            if not wids:
                raise StopChatFlow(f"There are not enough resources to deploy cpu: {cpu}, memory: {memory}.")

    def get_k8s_sshclient(self, private_key_path="/root/.ssh/id_rsa", user="rancher"):
        ssh_key = j.clients.sshkey.get(self.vdc_name)
        ssh_key.private_key_path = private_key_path
        ssh_key.load_from_file_system()
        ssh_client = j.clients.sshclient.get(
            self.vdc_name, user=user, host=self.vdc_info["master_ip"], sshkey=self.vdc_name
        )
        return ssh_client

    def is_port_exposed(self, ssh_client, src_port):
        rc, out, err = ssh_client.sshclient.run(f"sudo netstat -tulpn | grep :{src_port}", warn=True)
        if rc == 0:
            return True
        return False

    def _forward_ports(self, port_forwards=None):
        """
        portforwards = {"<SERVICE_NAME>": {"src":<src_port>, "dest": <dest_port>} }
        example: portforwards = {
            "mysql": {"src": 7070, "dest": 3306, "protocol": "TCP"},
            "redis": {"src": 6060, "dest", 6379, "protocol": "TCP"}
            }

        """
        ssh_client = self.get_k8s_sshclient()
        port_forwards = port_forwards or {}
        for service, ports in port_forwards.items():
            if ports.get("src") and ports.get("dest"):
                # Validate if the port not exposed
                if self.is_port_exposed(ssh_client, ports.get("src")):
                    j.logger.critical(
                        f"VDC: Can not expose service with port {ports.get('src')} using socat, port already in use"
                    )
                    raise StopChatFlow(
                        f"VDC: Can not expose service with port {ports.get('src')} using socat, port already in use"
                    )

                cluster_ip = self.k8s_client.execute_native_cmd(
                    f"kubectl get service/{service} -o jsonpath='{{.spec.clusterIP}}'"
                )
                if cluster_ip and j.sals.fs.exists("/root/.ssh/id_rsa"):
                    socat = "/var/lib/rancher/k3s/data/current/bin/socat"
                    cmd = f"{socat} tcp-listen:{ports['src']},reuseaddr,fork tcp:{cluster_ip}:{ports['dest']}"
                    template = f"""#!/sbin/openrc-run
                    name="{service}"
                    command="{cmd}"
                    pidfile="/var/run/{service}.pid"
                    command_background=true
                    """
                    template = dedent(template)
                    file_name = f"{self.config.release_name}-socat-{service}"
                    rc, out, err = ssh_client.sshclient.run(
                        f"sudo touch /etc/init.d/{file_name} && sudo chmod 777 /etc/init.d/{file_name} &&  echo '{template}' >> /etc/init.d/{file_name} && sudo rc-service {file_name} start",
                        warn=True,
                    )
                    if rc:
                        j.logger.critical(
                            f"VDC: Can not expose service using socat error was rc:{rc}, out:{out}, error:{err}"
                        )
                    return True
        return False

    def _ask_smtp_settings(self):
        form = self.new_form()
        smtp_host = form.string_ask("SMTP Host", default="smtp.gmail.com", required=True)
        smtp_port = form.string_ask("SMTP Port", default=587, required=True)
        smtp_username = form.string_ask("Email (SMTP username)", required=True)
        smtp_password = form.secret_ask("Email Password", required=True)
        form.ask()
        self.config.chart_config.smtp_host = smtp_host.value
        self.config.chart_config.smtp_port = smtp_port.value
        self.config.chart_config.smtp_username = smtp_username.value
        self.config.chart_config.smtp_password = smtp_password.value

    def _get_domain(self):
        # get domain for the ip address
        self.md_show_update("Preparing gateways ...")
        self.preferred_farm_gw = True
        gateways = {}

        # try preferred farm gateways first
        gateways = deployer.list_all_gateways(self.config.username, PREFERRED_FARM, identity_name=self.identity_name)
        if not gateways:
            self.preferred_farm_gw = False
            gateways = deployer.list_all_gateways(
                self.config.username, self.vdc_info["farm_name"], identity_name=self.identity_name
            )
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
                domains[domain] = gw_dict
                self.gateway_pool = gw_dict["pool"]
                self.gateway = gw_dict["gateway"]
                managed_domain = domain

                release_name = self.config.release_name.replace("_", "-")
                owner_prefix = self.config.username.replace(".3bot", "").replace(".", "").replace("_", "-")
                solution_type = self.SOLUTION_TYPE.replace(".", "").replace("_", "-")
                # check if domain name is free or append random number

                if self.config.chart_config.domain_type == "Choose a custom subdomain on a gateway":
                    self.custom_subdomain = self.string_ask(
                        f"Please enter a subdomain to be added to {managed_domain}", required=True, is_identifier=True
                    )
                    full_domain = f"{self.custom_subdomain}.{managed_domain}"
                else:
                    full_domain = f"{owner_prefix}-{solution_type}-{release_name}.{managed_domain}"

                metafilter = lambda metadata: metadata.get("owner") == self.config.username
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
                        self.config.chart_config.domain = full_domain
                        break
                    else:
                        if self.config.chart_config.domain_type == "Choose a custom subdomain on a gateway":
                            self.custom_subdomain = self.string_ask(
                                f"Please enter another subdomain as {self.custom_subdomain} is unavailable on {managed_domain}",
                                required=True,
                                is_identifier=True,
                            )
                            full_domain = f"{self.custom_subdomain}.{managed_domain}"
                        else:
                            random_number = random.randint(1000, 100_000)
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
                return self.config.chart_config.domain

        if not is_managed_domains:
            raise StopChatFlow("Couldn't find managed domains in the available gateways. Please contact support.")
        else:
            raise StopChatFlow(
                "No active gateways were found.Please contact support. The resources you paid for will be re-used in your upcoming deployments."
            )

    def _does_domain_point_to_ip(self, domain, ip):
        try:
            return j.sals.nettools.get_host_by_name(domain) == ip
        except TypeError:
            return False

    def _get_custom_domain(self):
        valid = False
        cluster_ip = self.vdc_info["public_ip"]
        while not valid:
            custom_domain = self.string_ask(
                f"Please enter the domain name, make sure the domain points to {cluster_ip}.", required=True
            )
            if not self._does_domain_point_to_ip(custom_domain, cluster_ip):
                self.md_show(f"The domain {custom_domain} doesn't point to {cluster_ip}.")
            else:
                valid = True
                self.config.chart_config.domain = custom_domain

    @deployment_context()
    def _create_subdomain(self):
        self.workload_ids = []
        metadata = {
            "name": self.config.release_name,
            "form_info": {"chatflow": self.SOLUTION_TYPE, "Solution name": self.config.release_name},
        }
        self.workload_ids.append(
            deployer.create_subdomain(
                pool_id=self.gateway_pool.pool_id,
                gateway_id=self.gateway.node_id,
                subdomain=self.config.chart_config.domain,
                addresses=[self.vdc_info["public_ip"]],
                solution_uuid=self.solution_id,
                identity_name=self.identity_name,
                **metadata,
            )
        )
        success = deployer.wait_workload(self.workload_ids[0], self)
        if not success:
            raise DeploymentFailed(
                f"Failed to create subdomain {self.config.chart_config.domain} on gateway {self.gateway.node_id} {self.workload_ids[0]}. The resources you paid for will be re-used in your upcoming deployments.",
                wid=self.workload_ids[0],
            )

    @chatflow_step(title="Preparing The Chatflow")
    def init_chatflow(self):
        self.md_show_update("Preparing the chatflow...")
        self._init_solution()
        self._get_kube_config()
        self.k8s_client = j.sals.kubernetes.Manager(config_path=self.vdc_info["kube_config_path"])

    @chatflow_step(title="Solution Name")
    def get_release_name(self):
        message = "Please enter a name for your solution (will be used in listing and deletions in the future and in having a unique url)"
        releases = [
            release["name"]
            for release in self.k8s_client.list_deployed_releases()
            if release["namespace"].startswith(self.chart_name)
        ]
        self.config.release_name = self.string_ask(
            message, required=True, is_identifier=True, not_exist=["solution name", releases], md=True, max_length=20
        )

    @chatflow_step(title="Solution Flavor")
    def choose_flavor(self):
        if hasattr(self, "CHART_LIMITS"):
            chart_limits = self.CHART_LIMITS
        else:
            chart_limits = CHART_LIMITS
        if hasattr(self, "RESOURCE_VALUE_TEMPLATE"):
            resource_template = self.RESOURCE_VALUE_TEMPLATE
        else:
            resource_template = RESOURCE_VALUE_TEMPLATE

        messages = []
        for flavor in chart_limits:
            flavor_specs = ""
            for key in chart_limits[flavor]:
                flavor_specs += f"{resource_template[key].format(chart_limits[flavor][key])} - "
            msg = f"{flavor} ({flavor_specs[:-3]})"
            messages.append(msg)
        chosen_flavor = self.single_choice(
            "Please choose the flavor you want to use (helm chart limits define how much resources the deployed solution will use)",
            options=messages,
            required=True,
            default=messages[0],
        )
        flavor = chosen_flavor.split()[0]
        self.config.chart_config.resources_limits.update(chart_limits[flavor])
        no_nodes = int(self.config.chart_config.resources_limits.get("no_nodes", 1))
        memory = int(self.config.chart_config.resources_limits["memory"][:-2])
        cpu = int(self.config.chart_config.resources_limits["cpu"][:-1])

        self._validate_resource_limits(cpu, memory, no_nodes)

    @chatflow_step(title="Create subdomain")
    def create_subdomain(self):
        choices = [
            "Choose subdomain for me on a gateway",
            "Choose a custom subdomain on a gateway",
            "Choose a custom domain",
        ]
        self.config.chart_config.domain_type = self.single_choice(
            "Select the domain type", choices, default="Choose subdomain for me on a gateway"
        )
        custom_domain = self.config.chart_config.domain_type == "Choose a custom domain"
        # get self.config.chart_config.domain
        if custom_domain:
            self._get_custom_domain()
        else:
            self._get_domain()
            self._create_subdomain()
        if custom_domain:
            self.config.chart_config.cert_resolver = "le"
        elif self.preferred_farm_gw:
            # subdomain selected on gateway on preferred farm
            self.config.chart_config.cert_resolver = "gridca"

    @chatflow_step(title="Chart Backup")
    def ask_backup(self):
        self.backup = self.single_choice(
            "Do you want to enable backup for this solution?", ["Yes", "No"], default="Yes", required=True
        )
        if self.backup == "No":
            self.config.chart_config.backup = ""

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
        chart_config = {
            "solution_uuid": self.solution_id,
            "threefoldVdc.backup": self.config.chart_config.backup,
            "global.ingress.certresolver": self.config.chart_config.cert_resolver,
            "resources.limits.cpu": self.config.chart_config.resources_limits["cpu"],
            "resources.limits.memory": self.config.chart_config.resources_limits["memory"],
        }
        custom_config = self.get_config()
        chart_config.update(custom_config)
        extra_config_string_safe = self.get_config_string_safe()
        try:
            self.k8s_client.install_chart(
                release=self.config.release_name,
                chart_name=f"{self.HELM_REPO_NAME}/{self.chart_name}",
                namespace=f"{self.chart_name}-{self.config.release_name}",
                extra_config=chart_config,
                extra_config_string_safe=extra_config_string_safe,
            )
        except Exception as e:
            stop_message = f"Helm install command failed, {e}"
            self.k8s_client.execute_native_cmd(
                f"helm delete -n {self.chart_name}-{self.config.release_name} {self.config.release_name}"
            )
            self.stop(dedent(stop_message))

    def chart_pods_started(self):
        pods_status_info = self.k8s_client.execute_native_cmd(
            cmd=f"kubectl --namespace {self.chart_name}-{self.config.release_name} get pods -l app.kubernetes.io/name={self.chart_name} -l app.kubernetes.io/instance={self.config.release_name} -o=jsonpath='{{.items[*].status.containerStatuses[*].ready}}'"
        )
        if "false" in pods_status_info or pods_status_info == "":
            return False
        return True

    def _has_domain(self):
        return getattr(self, "domain", None) is not None

    def get_pods(self, pattern):
        """Get the pods we need including this pattern

        Args:
            pattern(string) : pattern used during selecting the desired pod
        Returns:
            list(string) : Pods we got with the specified pattern
        """
        pods_info = self.k8s_client.execute_native_cmd(
            f"kubectl get pods --no-headers -o custom-columns=':metadata.name' -n {self.chart_name}-{self.config.release_name} | grep {pattern}"
        )
        return pods_info.splitlines()

    def exec_command_in_pod(self, pod_name, command):
        """Takes command to be executed on a pod

        Args:
            pod_name(string) : Name of the pod we want to execute the command on
            command (string) : Command you want to execute on the specified pod
        Returns:
            string : Output of the command
        """

        return self.k8s_client.execute_native_cmd(
            f'kubectl -n {self.chart_name}-{self.config.release_name} exec {pod_name} -- bash -c "{command}"'
        )

    def chart_resource_failure(self):
        pods_info = self.k8s_client.execute_native_cmd(
            cmd=f"kubectl --namespace {self.chart_name}-{self.config.release_name} get pods -l app.kubernetes.io/name={self.chart_name} -l app.kubernetes.io/instance={self.config.release_name} -o=jsonpath='{{.items[*].status.conditions[*].message}}'"
        )  # Gets the last event message
        if "Insufficient" in pods_info:
            return True
        return False

    def rollback(self):
        self.k8s_client.execute_native_cmd(f"kubectl delete ns {self.chart_name}-{self.config.release_name}")
        j.sals.marketplace.solutions.cancel_solution_by_uuid(self.solution_id)

    @chatflow_step(title="Initializing", disable_previous=True)
    def initializing(self, timeout=800, pod_initalizing_timeout=POD_INITIALIZING_TIMEOUT):
        self.md_show_update(f"Initializing your {self.SOLUTION_TYPE}...")
        domain_message = ""
        if self.config.chart_config.domain:
            domain_message = f"Domain: {self.config.chart_config.domain}"
        error_message_template = f"""\
                Failed to initialize {self.SOLUTION_TYPE}, please contact support with this information:
                {domain_message}
                VDC Name: {self.vdc_name}
                Farm name: {self.vdc_info["farm_name"]}
                Reason: {{reason}}
                """
        start_time = time()
        while time() - start_time <= pod_initalizing_timeout:
            if self.chart_pods_started():
                break
            gevent.sleep(1)

        if self.chart_resource_failure():
            stop_message = error_message_template.format(
                reason="Couldn't find resources in the cluster for the solution"
            )
            self.rollback()
            self.stop(dedent(stop_message))

        if not self.chart_pods_started():
            stop_message = error_message_template.format(reason="Pods initialization timed out")
            self.rollback()
            self.stop(dedent(stop_message))

        if self.config.chart_config.domain and not j.sals.reservation_chatflow.wait_http_test(
            f"https://{self.config.chart_config.domain}", timeout=timeout - POD_INITIALIZING_TIMEOUT, verify=False
        ):
            stop_message = error_message_template.format(reason="Couldn't reach the website after deployment")
            self.rollback()
            self.stop(dedent(stop_message))
        self._label_resources(backupType="vdc")

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self, extra_info=""):
        domain_message = ""
        if self.config.chart_config.domain:
            domain_message = f'- You can access it via the browser using: <a href="https://{self.config.chart_config.domain}" target="_blank">https://{self.config.chart_config.domain}</a><br />\n'
        message = f"""\
        # You deployed a new instance {self.config.release_name} of {self.SOLUTION_TYPE}
        <br />\n
        {domain_message}
        {extra_info}
        """
        self.md_show(dedent(message), md=True)

    def _label_resources(self, resources=None, **kwargs):
        if not kwargs:
            return
        resources = resources or "deployment,rs,svc,sts,ds,cm,secret,ing,pv,pvc,sc"
        namespace = f"{self.chart_name}-{self.config.release_name}"
        all_resources_json = self.k8s_client.execute_native_cmd(f"kubectl get {resources} -n {namespace} -o json")
        all_resources = j.data.serializers.json.loads(all_resources_json)
        for resource in all_resources.get("items", []):
            kind = resource.get("kind", "").lower()
            name = resource.get("name", "")
            if not name:
                name = resource.get("metadata", {}).get("name", "")
            if not all([name, kind]):
                j.logger.warning(f"can't retrieve resource info of {list(resource.keys())}")
                continue
            for key, val in kwargs.items():
                self.k8s_client.execute_native_cmd(
                    f"kubectl label {kind} {name} -n {namespace} {key}={val} --overwrite"
                )

    def generate_signing_key(self):
        k = nacl.signing.SigningKey.generate()
        return k.encode(encoder=nacl.encoding.Base64Encoder).decode()
