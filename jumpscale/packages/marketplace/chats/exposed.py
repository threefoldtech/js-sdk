import uuid

from jumpscale.loader import j
from jumpscale.packages.tfgrid_solutions.chats.solution_expose import SolutionExpose as BaseSolutionExpose
from jumpscale.sals.chatflows.chatflows import StopChatFlow, chatflow_step
from jumpscale.sals.marketplace import MarketPlaceChatflow, deployer, solutions

kinds = {
    "minio": solutions.list_minio_solutions,
    "kubernetes": solutions.list_kubernetes_solutions,
    "ubuntu": solutions.list_ubuntu_solutions,
    "flist": solutions.list_flist_solutions,
    "gitea": solutions.list_gitea_solutions,
}


class SolutionExpose(BaseSolutionExpose, MarketPlaceChatflow):
    @chatflow_step(title="")
    def deployment_start(self):
        self._validate_user()
        super().deployment_start()
        self.solution_metadata["owner"] = self.user_info()["username"]

    @chatflow_step(title="Solution type")
    def solution_type(self):
        self.kind = self.single_choice("Please choose the solution type", list(kinds.keys()), required=True)
        solutions = kinds[self.kind](self.solution_metadata["owner"])
        self.sols = {}
        for sol in solutions:
            name = sol["Name"]
            self.sols[name] = sol

    @chatflow_step(title="Domain")
    def domain(self):
        # {"domain": {"gateway": gw, "pool": p}}

        gateways = deployer.list_all_gateways(self.solution_metadata["owner"])
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
                messages[f"Managed {dom}"] = gw_dict

        # add delegate domains
        delegated_domains = solutions.list_delegated_domain_solutions(self.solution_metadata["owner"])
        for dom in delegated_domains:
            gw_dict = {"gateway": gateway_id_dict[dom["Gateway"]], "pool": pool_id_dict[dom["Pool"]]}
            messages[f"Delegated {dom['Name']}"] = gw_dict

        domain_ask_list = list(messages.keys())
        # add custom_domain
        domain_ask_list.append("Custom Domain")
        chosen_domain = self.single_choice("Please choose the domain you wish to use", domain_ask_list, required=True,)
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
                )
                if "." in domain:
                    retry = True
                    self.md_show("You can't nest domains. please click next to try again")
                else:
                    if j.tools.dnstool.is_free(domain + "." + self.domain):
                        break
                    else:
                        self.md_show(f"domain {domain + '.' + self.domain} is not available")

            self.domain = domain + "." + self.domain
        else:
            self.domain = self.string_ask("Please specify the domain name you wish to bind to:", required=True,)
            self.domain_gateway, self.domain_pool = deployer.select_gateway(self.solution_metadata["owner"], self)
            self.domain_type = "Custom Domain"
            res = """\
            Please create a `CNAME` record in your dns manager for domain: `{{domain}}` pointing to:
            {% for dns in gateway.dns_nameserver -%}
            - {{dns}}
            {% endfor %}
            """
            res = j.tools.jinja2.render_template(template_text=res, gateway=self.domain_gateway, domain=self.domain)
            self.md_show(res)
        self.name_server = self.domain_gateway.dns_nameserver[0]
        self.secret = f"{j.core.identity.me.tid}:{uuid.uuid4().hex}"


chat = SolutionExpose
