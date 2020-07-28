import uuid

from jumpscale.clients.explorer.models import Category
from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step, StopChatFlow
from jumpscale.sals.reservation_chatflow.models import SolutionType
from jumpscale.sals.reservation_chatflow import deployer, solutions

kinds = {
    "minio": j.sals.reservation_chatflow.solutions.list_minio_solutions,
    "kubernetes": j.sals.reservation_chatflow.solutions.list_kubernetes_solutions,
    "ubuntu": j.sals.reservation_chatflow.solutions.list_ubuntu_solutions,
    "flist": j.sals.reservation_chatflow.solutions.list_flist_solutions,
    "gitea": j.sals.reservation_chatflow.solutions.list_gitea_solutions,
}

domain_types = {"delegate": Category.Domain_delegate, "sub": Category.Subdomain}

ports = {"minio": 9000, "kubernetes": 6443, "gitea": 3000}


class SolutionExpose(GedisChatBot):
    steps = [
        "deployment_start",
        "solution_type",
        "exposed_solution",
        "exposed_ports",
        "domain_1",
        "domain_2",
        "confirmation",
        "reservation",
        "success",
    ]
    title = "Solution Expose"

    @chatflow_step(title="")
    def deployment_start(self):
        self.solution_id = uuid.uuid4().hex
        self.user_form_data = {}
        self.md_show("# This wizard will help you expose a deployed solution using the web gateway")

    @chatflow_step(title="Solution type")
    def solution_type(self):
        self.kind = self.single_choice("Please choose the solution type", list(kinds.keys()), required=True)
        solutions = kinds[self.kind]()
        self.sols = {}
        for sol in solutions:
            name = sol["Name"]
            self.sols[name] = sol

    @chatflow_step(title="Solution to be exposed")
    def exposed_solution(self):
        self.solution_name = self.single_choice(
            "Please choose the solution to expose", list(self.sols.keys()), required=True
        )
        self.solution = self.sols[self.solution_name]
        self.pool_id = self.solution["Pool"]

    @chatflow_step(title="Ports")
    def exposed_ports(self):
        port = ports.get(self.kind)
        form = self.new_form()
        tlsport = form.int_ask("Which tls port you want to expose", default=port or 443)
        port = form.int_ask("Which port you want to expose", default=port or 80)
        form.ask()
        self.port = port.value
        self.tls_port = tlsport.value
        if self.kind == "kubernetes":
            self.solution_ip = self.solution["Master IP"]
        elif self.kind == "minio":
            self.solution_ip = self.solution["Primary IPv4"]
        else:
            self.solution_ip = self.solution["IPv4 Address"]

    @chatflow_step(title="Domain 1")
    def domain_1(self):
        self.gateways = deployer.list_pool_gateways(self.pool_id)
        domain_ask_list = []
        self.user_domains = {}
        for dom in deployer.workloads["DEPLOY"]["DOMAIN-DELEGATE"][self.pool_id]:
            domain_ask_list.append(f"Delegated Domain: {dom.domain}")
            self.user_domains[dom.domain] = dom
        self.managed_domains = {}
        for gateway in self.gateways.values():
            for dom in gateway.managed_domains:
                self.managed_domains[dom] = gateway
                domain_ask_list.append(f"Managed Domain: {dom}")
        domain_ask_list.append("Custom Domain")
        self.chosen_domain = self.single_choice("Please choose the domain you wish to use", domain_ask_list)

    @chatflow_step(title="Domain 2")
    def domain_2(self):
        if self.chosen_domain == "Custom Domain":
            self.domain = self.string_ask("Please specify the domain name you wish to bind to:")
            self.domain_gateway = deployer.select_gateway(self, self.pool_id)
            res = """\
            Please create a `CNAME` record in your dns manager for domain: `{{domain}}` pointing to:
            {% for dns in gateway.dns_nameserver -%}
            - {{dns}}
            {% endfor %}
            """
            res = j.tools.jinja2.render_template(template_text=res, gateway=self.domain_gateway, domain=self.domain)
            self.md_show(res)

        else:
            temp = self.chosen_domain.split()
            domain_type = temp[0]
            domain_name = temp[-1]
            if domain_type == "Managed":
                self.domain_gateway = self.managed_domains[domain_name]
            elif domain_type == "Delegated":
                domain_obj = self.user_domains[domain_name]
                self.domain_gateway = deployer._explorer.gateway.get(domain_obj.info.node_id)
            retry = False
            while True:
                domain = self.string_ask(
                    f"Please specify the sub domain name you wish to bind to. will be (subdomain).{domain_name}",
                    retry=retry,
                )
                if "." in domain:
                    retry = True
                    self.md_show("You can't nest domains. please click next to try again")
                else:
                    break
            self.domain = domain + "." + domain_name
            self.name_server = self.domain_gateway.dns_nameserver[0]
            self.gateway_id = self.domain_gateway.node_id
            self.secret = f"{j.core.identity.me.tid}:{uuid.uuid4().hex}"

    @chatflow_step(title="Confirmation", disable_previous=True)
    def confirmation(self):
        self.metadata = {
            "Exposed Solution": self.solution_name,
            "Solution Type": self.kind,
            "Solution Exposed IP": self.solution_ip,
            "Port": self.port,
            "TLS Port": self.tls_port,
            "Gateway": self.gateway_id,
            "Pool": self.pool_id,
            "TRC Secret": self.secret,
        }
        self.md_show_confirm(self.metadata, html=True)

    @chatflow_step(title="Reservation", disable_previous=True)
    def reservation(self):
        metadata = {"name": self.domain, "form_info": {"Solution name": self.domain, "chatflow": "exposed"}}
        query = {"mru": 1, "cru": 1, "sru": 1}
        self.selected_node = deployer.schedule_container(self.pool_id, **query)
        self.network_name = self.solution["Network"]

        result = deployer.add_network_node(self.network_name, self.selected_node, self.pool_id)
        if result:
            for wid in result["ids"]:
                success = deployer.wait_workload(wid, self)
                if not success:
                    raise StopChatFlow(f"Failed to add node to network {wid}")

        self.network_view = deployer.get_network_view(self.network_name)
        self.tcprouter_ip = self.network_view.get_free_ip(self.selected_node)
        if not self.tcprouter_ip:
            raise StopChatFlow(
                f"No available ips one for network {self.network_view.name} node {self.selected_node.node_id}"
            )

        if self.chosen_domain != "Custom":
            self.dom_id = deployer.create_subdomain(
                pool_id=self.pool_id,
                gateway_id=self.gateway_id,
                subdomain=self.domain,
                **metadata,
                solution_uuid=self.solution_id,
            )
            success = deployer.wait_workload(self.dom_id)
            if not success:
                j.sal.chatflow_solutions.cancel_solution([self.dom_id])
                raise StopChatFlow(f"Failed to reserve sub-domain workload {self.dom_id}")

        self.proxy_id = deployer.create_proxy(
            pool_id=self.pool_id,
            gateway_id=self.gateway_id,
            domain_name=self.domain,
            trc_secret=self.secret,
            **metadata,
            solution_uuid=self.solution_id,
        )
        success = deployer.wait_workload(self.proxy_id, self)
        if not success:
            j.sal.chatflow_solutions.cancel_solution([self.proxy_id])
            raise StopChatFlow(f"Failed to reserve reverse proxy workload {self.proxy_id}")

        self.tcprouter_id = deployer.expose_address(
            pool_id=self.pool_id,
            gateway_id=self.gateway_id,
            network_name=self.network_name,
            local_ip=self.solution_ip,
            port=self.port,
            tls_port=self.tls_port,
            trc_secret=self.secret,
            bot=self,
            **metadata,
            solution_uuid=self.solution_id,
        )
        success = deployer.wait_workload(self.tcprouter_id)
        if not success:
            j.sal.chatflow_solutions.cancel_solution([self.tcprouter_id])
            raise StopChatFlow(f"Failed to reserve tcprouter container workload {self.tcprouter_id}")

    @chatflow_step(title="Success", disable_previous=True)
    def success(self):
        res_md = f"Use this Gateway to connect to your exposed solution `{self.domain}`"
        self.md_show(res_md)


chat = SolutionExpose
