import math
import time
import uuid
from textwrap import dedent

from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.reservation_chatflow import deployer, solutions
from jumpscale.sals.reservation_chatflow.models import SolutionType


class GollumDeploy(GedisChatBot):
    steps = [
        "gollum_name",
        "container_resources",
        "select_pool",
        "gollum_network",
        "public_key_get",
        "gollum_email",
        "github_repo_setup",
        "container_node_id",
        "container_ip",
        "select_domain",
        "reservation",
        "container_access",
    ]
    title = "Gollum"

    def _gollum_start(self):
        self.username = self.user_info()["username"]
        self.solution_id = uuid.uuid4().hex
        self.flist_url = "https://hub.grid.tf/asamir.3bot/14443-gollum-new.flist"
        self.user_form_data = dict()
        self.user_form_data["chatflow"] = "gollum"
        self.threebot_name = j.data.text.removesuffix(self.username, ".3bot")
        self.solution_metadata = {}

    @chatflow_step(title="Solution Name")
    def gollum_name(self):
        self._gollum_start()
        valid = False
        while not valid:
            self.solution_name = deployer.ask_name(self)
            monitoring_solutions = solutions.list_gollum_solutions(sync=False)
            valid = True
            for sol in monitoring_solutions:
                if sol["Name"] == self.solution_name:
                    valid = False
                    self.md_show("The specified solution name already exists. please choose another name.")
                    break
                valid = True

    @chatflow_step(title="Container resources")
    def container_resources(self):
        self.resources = deployer.ask_container_resources(self)

    @chatflow_step(title="Pool")
    def select_pool(self):
        query = {
            "cru": self.resources["cpu"],
            "mru": math.ceil(self.resources["memory"] / 1024),
            "sru": math.ceil(self.resources["disk_size"] / 1024),
        }
        cloud_units = deployer.calculate_capacity_units(**query)
        self.pool_id = deployer.select_pool(self, cu=cloud_units.cu, su=cloud_units.su)

    @chatflow_step(title="Network")
    def gollum_network(self):
        self.network_view = deployer.select_network(self)

    @chatflow_step(title="Access Key")
    def public_key_get(self):
        self.public_key = self.upload_file(
            """Please upload your public SSH key to be able to access the deployed container via ssh""", required=True
        ).strip()

    @chatflow_step(title="Email")
    def gollum_email(self):
        form = self.new_form()
        # TODO: replace by email_ask to verify email
        self.email = form.string_ask("Please enter an email to get ssl certificate updates of your container")
        form.ask()

    @chatflow_step(title="Github repo setup")
    def github_repo_setup(self):
        form = self.new_form()
        self.github_user = form.string_ask("Please enter your github username")
        # TODO: replace by email_ask to verify email
        self.github_email = form.string_ask("Please enter your github email")
        self.github_repo = form.string_ask(
            "Please enter your github repo name that will be used for the wiki.# Make sure the repo exists"
        )
        self.github_token = form.string_ask(
            "Please enter github personal access token."
            "You can create it by following the steps here: https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token"
        )
        form.ask()

    @chatflow_step(title="Choose a node to deploy on")
    def container_node_id(self):
        query = {
            "cru": self.resources["cpu"],
            "mru": math.ceil(self.resources["memory"] / 1024),
            "sru": self.resources["disk_size"],
        }
        self.selected_node = deployer.ask_container_placement(self, self.pool_id, **query)
        if not self.selected_node:
            self.selected_node = deployer.schedule_container(self.pool_id, **query)

    @chatflow_step(title="Container IP")
    def container_ip(self):
        self.network_view_copy = self.network_view.copy()
        result = deployer.add_network_node(
            self.network_view.name,
            self.selected_node,
            self.pool_id,
            self.network_view_copy,
            bot=self,
            **self.solution_metadata,
        )
        if result:
            for wid in result["ids"]:
                success = deployer.wait_workload(wid, self, breaking_node_id=self.selected_node.node_id)
                if not success:
                    raise StopChatFlow(f"Failed to add node {self.selected_node.node_id} to network {wid}")
            self.network_view_copy = self.network_view_copy.copy()
        free_ips = self.network_view_copy.get_node_free_ips(self.selected_node)
        self.ip_address = self.drop_down_choice("Please choose IP Address for your solution", free_ips)

    @chatflow_step(title="Domain")
    def select_domain(self):
        gateways = deployer.list_all_gateways()
        if not gateways:
            raise StopChatFlow("There are no available gateways in the farms bound to your pools.")

        domains = dict()
        for gw_dict in gateways.values():
            gateway = gw_dict["gateway"]
            for domain in gateway.managed_domains:
                domains[domain] = gw_dict

        self.domain = self.single_choice(
            "Please choose the domain you wish to use", list(domains.keys()), required=True
        )

        self.gateway = domains[self.domain]["gateway"]
        self.gateway_pool = domains[self.domain]["pool"]
        self.domain = f"{self.threebot_name}-{self.solution_name}.{self.domain}"
        self.domain = j.sals.zos.get().gateway.correct_domain(self.domain)

        self.addresses = []
        for ns in self.gateway.dns_nameserver:
            self.addresses.append(j.sals.nettools.get_host_by_name(ns))

        self.secret = f"{j.core.identity.me.tid}:{uuid.uuid4().hex}"

    @chatflow_step(title="Reservation")
    def reservation(self):
        self.workload_ids = []
        metadata = {
            "name": self.solution_name,
            "form_info": {"chatflow": "gollum", "Solution name": self.solution_name},
        }
        self.solution_metadata.update(metadata)

        # reserve subdomain
        self.workload_ids.append(
            deployer.create_subdomain(
                pool_id=self.pool_id,
                gateway_id=self.gateway.node_id,
                subdomain=self.domain,
                addresses=self.addresses,
                solution_uuid=self.solution_id,
                **self.solution_metadata,
            )
        )
        success = deployer.wait_workload(self.workload_ids[0], self)
        if not success:
            raise StopChatFlow(
                f"Failed to create subdomain {self.domain} on gateway {self.gateway.node_id} {self.workload_ids[0]}"
            )

        # expose container domain
        wid, _ = deployer.expose_address(
            pool_id=self.pool_id,
            gateway_id=self.gateway.node_id,
            network_name=self.network_view.name,
            local_ip=self.ip_address,
            port=80,
            tls_port=443,
            trc_secret=self.secret,
            node_id=self.selected_node.node_id,
            reserve_proxy=True,
            domain_name=self.domain,
            proxy_pool_id=self.gateway_pool.pool_id,
            solution_uuid=self.solution_id,
            **self.solution_metadata,
        )
        self.workload_ids.append(wid)
        success = deployer.wait_workload(self.workload_ids[1], self)
        if not success:
            solutions.cancel_solution(self.workload_ids)
            raise StopChatFlow(
                f"Failed to create TRC container on node {self.selected_node.node_id} {self.workload_ids[1]}"
            )
        self.container_url = f"https://{self.domain}/"

        # deploy container
        var_dict = {
            "pub_key": self.public_key,
            "GITHUB_USER": self.github_user.value,
            "GITHUB_EMAIL": self.github_email.value,
            "GITHUB_REPO": self.github_repo.value,
            "GITHUB_TOKEN": self.github_token.value,
        }
        entrypoint = f'/bin/bash /start.sh "{self.domain}" "{self.email}"'
        self.workload_ids.append(
            deployer.deploy_container(
                pool_id=self.pool_id,
                node_id=self.selected_node.node_id,
                network_name=self.network_view.name,
                ip_address=self.ip_address,
                flist=self.flist_url,
                cpu=self.resources["cpu"],
                memory=self.resources["memory"],
                disk_size=self.resources["disk_size"],
                env=var_dict,
                interactive=False,
                entrypoint=entrypoint,
                solution_uuid=self.solution_id,
                **self.solution_metadata,
            )
        )
        success = deployer.wait_workload(self.workload_ids[2], self)
        if not success:
            raise StopChatFlow(
                f"Failed to create container on node {self.selected_node.node_id} {self.workload_ids[2]}"
            )

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def container_access(self):
        res = f"""\
        # Gollum has been deployed successfully:
        <br />\n
        Reservation id: {self.workload_ids[-1]}

        To ssh into your container: ```ssh root@{self.ip_address}```

        You can access your wiki repo from browser at {self.container_url}

        ## It may take a few minutes...
        """
        self.md_show(dedent(res), md=True)


chat = GollumDeploy
