import uuid
from textwrap import dedent
from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step, StopChatFlow
from jumpscale.sals.reservation_chatflow import deployer, solutions, deployment_context, DeploymentFailed

kinds = {
    "minio": solutions.list_minio_solutions,
    "kubernetes": solutions.list_kubernetes_solutions,
    "ubuntu": solutions.list_ubuntu_solutions,
    "flist": solutions.list_flist_solutions,
    "gitea": solutions.list_gitea_solutions,
}

ports = {"minio": 9000, "kubernetes": 6443, "gitea": 3000}


class SolutionExpose(GedisChatBot):
    steps = [
        "solution_type",
        "exposed_solution",
        "expose_type",
        "exposed_ports",
        "domain_selection",
        "reservation",
        "success",
    ]
    title = "Solution Expose"

    def _deployment_start(self):
        self.solution_id = uuid.uuid4().hex
        self.user_form_data = {}
        self.solution_metadata = {}
        self.email = self.user_info()["email"]
        self.username = self.user_info()["username"]
        self.threebot_name = j.data.text.removesuffix(self.username, ".3bot")

    @chatflow_step(title="Solution type")
    def solution_type(self):
        self.md_show_update("Initializing chatflow....")
        self._deployment_start()

        available_solutions = {}
        for kind in list(kinds.keys()):
            solutions = kinds[kind]()
            if solutions:
                available_solutions.update({kind: solutions})

        if not available_solutions:
            raise StopChatFlow(f"You don't have any solutions to expose")

        self.kind = self.single_choice(
            "Please choose the solution type", list(available_solutions.keys()), required=True
        )
        self.sols = {}
        for sol in available_solutions[self.kind]:
            name = sol["Name"]
            self.sols[name] = sol

    @chatflow_step(title="Solution to be exposed")
    def exposed_solution(self):
        self.solution_name = self.single_choice(
            "Please choose the solution to expose", list(self.sols.keys()), required=True
        )
        self.solution = self.sols[self.solution_name]
        if self.kind == "kubernetes":
            self.pool_id = self.solution["Master Pool"]
        elif self.kind == "minio":
            self.pool_id = self.solution["Primary Pool"]
        else:
            self.pool_id = self.solution["Pool"]

    @chatflow_step(title="Expose Type")
    def expose_type(self):
        choices = ["TRC", "NGINX"]
        self.proxy_type = self.single_choice(
            "Select how you want to expose your solution (TRC forwards the traffic as is to the specified HTTP/HTTPS ports while NGINX reverse proxies the HTTP/HTTPS requests to an HTTP port)",
            choices,
            default="TRC",
        )
        if self.proxy_type == "NGINX":
            force_https = self.single_choice("Do you want to force HTTPS?", ["YES", "NO"], default="NO")
            self.force_https = force_https == "YES"

    @chatflow_step(title="Ports")
    def exposed_ports(self):
        port = ports.get(self.kind)
        if self.proxy_type == "TRC":
            form = self.new_form()
            tlsport = form.int_ask("Which tls port you want to expose", default=port or 443, required=True, min=1)
            port = form.int_ask("Which port you want to expose", default=port or 80, required=True, min=1)
            form.ask()
            self.port = port.value
            self.tls_port = tlsport.value
        elif self.proxy_type == "NGINX":
            self.port = self.int_ask("Which port you want to expose", default=port or 80, required=True, min=1)
        if self.kind == "kubernetes":
            self.solution_ip = self.solution["Master IP"]
        elif self.kind == "minio":
            self.solution_ip = self.solution["Primary IPv4"]
        else:
            self.solution_ip = self.solution["IPv4 Address"]

    @chatflow_step(title="Domain")
    def domain_selection(self):
        # {"domain": {"gateway": gw, "pool": p}}

        gateways = deployer.list_all_gateways()
        if not gateways:
            raise StopChatFlow("There are no available gateways in the farms bound to your pools")

        # add managed domains
        gateway_id_dict = {}
        pool_id_dict = {}
        messages = {}
        for gw_dict in gateways.values():
            gateway_id_dict[gw_dict["gateway"].node_id] = gw_dict["gateway"]
            pool_id_dict[gw_dict["pool"].pool_id] = gw_dict["pool"]
            for dom in gw_dict["gateway"].managed_domains:
                location_list = [
                    gw_dict["gateway"].location.continent,
                    gw_dict["gateway"].location.country,
                    gw_dict["gateway"].location.city,
                ]
                location = " - ".join([info for info in location_list if info and info != "Unknown"])
                if location:
                    location = f" Location: {location}"
                messages[f"Managed {dom}{location}"] = gw_dict

        # add delegate domains
        delegated_domains = solutions.list_delegated_domain_solutions()
        for dom in delegated_domains:
            if dom["Pool"] not in pool_id_dict:
                pool_id_dict[dom["Pool"]] = gateway_id_dict[dom["Gateway"]]
            gw_dict = {"gateway": gateway_id_dict[dom["Gateway"]], "pool": pool_id_dict[dom["Pool"]]}
            messages[f"Delegated {dom['Name']}"] = gw_dict

        domain_ask_list = list(messages.keys())
        # add custom_domain
        domain_ask_list.append("Custom Domain")
        chosen_domain = self.single_choice("Please choose the domain you wish to use", domain_ask_list, required=True)
        if chosen_domain != "Custom Domain":
            self.domain_gateway = messages[chosen_domain]["gateway"]
            self.domain_pool = messages[chosen_domain]["pool"]
            splits = chosen_domain.split()
            self.domain_type = splits[0]
            self.domain = splits[1]
            retry = False
            while True:
                domain = self.string_ask(
                    f"Please specify the sub domain name you wish to bind to. will be (subdomain).{self.domain}",
                    retry=retry,
                    required=True,
                    is_identifier=True,
                )
                domain = j.sals.zos.get().gateway.correct_domain(domain)
                if "." in domain:
                    retry = True
                    self.md_show("You can't nest domains. please click next to try again.")
                else:
                    if j.tools.dnstool.is_free(domain + "." + self.domain):
                        break
                    else:
                        self.md_show(f"domain {domain + '.' + self.domain} is not available.")

            self.domain = domain + "." + self.domain
        else:
            self.domain = self.string_ask("Please specify the domain name you wish to bind to:", required=True)
            self.domain = j.sals.zos.get().gateway.correct_domain(self.domain)
            self.domain_gateway, self.domain_pool = deployer.select_gateway(self)
            self.domain_type = "Custom Domain"
            res = """\
            Please create a `CNAME` record in your DNS manager for domain: `{{domain}}` pointing to:
            {% for dns in gateway.dns_nameserver -%}
            - {{dns}}
            {% endfor %}
            """
            res = j.tools.jinja2.render_template(template_text=res, gateway=self.domain_gateway, domain=self.domain)
            self.md_show(dedent(res), md=True)
        self.name_server = self.domain_gateway.dns_nameserver[0]
        self.secret = f"{j.core.identity.me.tid}:{uuid.uuid4().hex}"

    @chatflow_step(title="Reservation", disable_previous=True)
    @deployment_context()
    def reservation(self):
        metadata = {"name": self.domain, "form_info": {"Solution name": self.domain, "chatflow": "exposed"}}
        self.solution_metadata.update(metadata)
        query = {"mru": 1, "cru": 1, "sru": 1}
        self.selected_node = deployer.schedule_container(self.pool_id, **query)
        self.network_name = self.solution["Network"]

        result = deployer.add_network_node(
            self.network_name, self.selected_node, self.pool_id, bot=self, owner=self.solution_metadata.get("owner")
        )
        if result:
            for wid in result["ids"]:
                success = deployer.wait_workload(wid, self, breaking_node_id=self.selected_node.node_id)
                if not success:
                    raise DeploymentFailed(f"Failed to add node to network {wid}", wid=wid)

        self.network_view = deployer.get_network_view(self.network_name)
        self.tcprouter_ip = self.network_view.get_free_ip(self.selected_node)
        if not self.tcprouter_ip:
            raise StopChatFlow(
                f"No available ips one for network {self.network_view.name} node {self.selected_node.node_id}"
            )

        if self.domain_type != "Custom Domain":
            self.dom_id = deployer.create_subdomain(
                pool_id=self.domain_pool.pool_id,
                gateway_id=self.domain_gateway.node_id,
                subdomain=self.domain,
                **self.solution_metadata,
                solution_uuid=self.solution_id,
            )
            success = deployer.wait_workload(self.dom_id, self)
            if not success:
                raise DeploymentFailed(
                    f"Failed to reserve sub-domain workload {self.dom_id}", solution_uuid=self.solution_id
                )

        if self.proxy_type == "TRC":
            self.proxy_id = deployer.create_proxy(
                pool_id=self.domain_pool.pool_id,
                gateway_id=self.domain_gateway.node_id,
                domain_name=self.domain,
                trc_secret=self.secret,
                **self.solution_metadata,
                solution_uuid=self.solution_id,
            )
            success = deployer.wait_workload(self.proxy_id, self)
            if not success:
                raise DeploymentFailed(
                    f"Failed to reserve reverse proxy workload {self.proxy_id}", solution_uuid=self.solution_id
                )

        trc_log_config = j.core.config.get("LOGGING_SINK", {})
        if trc_log_config:
            trc_log_config["channel_name"] = f"{self.threebot_name}-{self.solution_name}-trc".lower()

        if self.proxy_type == "NGINX":
            self.tcprouter_id, _ = deployer.expose_and_create_certificate(
                domain=self.domain,
                email=self.email,
                pool_id=self.pool_id,
                gateway_id=self.domain_gateway.node_id,
                network_name=self.network_name,
                solution_ip=self.solution_ip,
                solution_port=self.port,
                trc_secret=self.secret,
                bot=self,
                enforce_https=self.force_https,
                log_config=trc_log_config,
                **self.solution_metadata,
                solution_uuid=self.solution_id,
            )
        else:
            self.tcprouter_id, _ = deployer.expose_address(
                pool_id=self.pool_id,
                gateway_id=self.domain_gateway.node_id,
                network_name=self.network_name,
                local_ip=self.solution_ip,
                port=self.port,
                tls_port=self.tls_port,
                trc_secret=self.secret,
                bot=self,
                log_config=trc_log_config,
                **self.solution_metadata,
                solution_uuid=self.solution_id,
            )
        success = deployer.wait_workload(self.tcprouter_id, self)
        if not success:
            raise DeploymentFailed(
                f"Failed to reserve TCP Router container workload {self.tcprouter_id}",
                solution_uuid=self.solution_id,
                wid=self.tcprouter_id,
            )

    def _determine_solution_protocol(self, timeout=60):
        def _get_protocol():
            prots = ["https", "http"]
            for prot in prots:
                if j.sals.nettools.wait_http_test(f"{prot}://{self.domain}", 5, verify=False):
                    return prot
            return None

        start_time = j.data.time.now()
        while (j.data.time.now() - start_time).seconds < timeout:
            if _get_protocol() is not None:
                return _get_protocol()
        return "https"

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        protocol = self._determine_solution_protocol()
        message = f"""\
        # Congratulations! Your solution has been exposed successfully:
        <br />\n
        - You can access it via the browser using: <a href="{protocol}://{self.domain}" target="_blank">{protocol}://{self.domain}</a>
        """
        self.md_show(dedent(message), md=True)


chat = SolutionExpose
