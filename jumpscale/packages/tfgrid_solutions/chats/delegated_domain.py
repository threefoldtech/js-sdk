import uuid
from textwrap import dedent

from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.reservation_chatflow import deployer


class DomainDelegation(GedisChatBot):
    steps = ["select_pool", "domain_name", "reservation", "success"]
    title = "Domain Delegation"

    @chatflow_step(title="Gateway Selection")
    def select_pool(self):
        deployer.chatflow_pools_check()
        self.solution_id = uuid.uuid4().hex
        self.gateway, pool = deployer.select_gateway(bot=self)
        self.pool_id = pool.pool_id
        self.solution_metadata = {}

    @chatflow_step(title="Domain delegation name")
    def domain_name(self):
        self.domain = self.string_ask("Please enter a domain name to delegate", required=True)
        self.gateway_id = self.gateway.node_id
        self.solution_metadata.update({"SolutionName": self.domain, "ٍSolutionType": "domain_delegate"})

    @chatflow_step(title="Reservation")
    def reservation(self):
        self.resv_id = deployer.delegate_domain(
            self.pool_id, self.gateway_id, self.domain, **self.solution_metadata, solution_uuid=self.solution_id
        )
        success = deployer.wait_workload(self.resv_id, self)
        if not success:
            raise StopChatFlow(f"Failed to deploy workload {self.resv_id}")

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        res = """\
        # Delegated your domain successfully:
        <br />\n
        - Please create an `NS` record in your dns manager for domain: `{{domain}}` pointing to:
            {% for dns in gateway.dns_nameserver -%}
            - {{dns}}
            {% endfor %}
            """
        res = j.tools.jinja2.render_template(
            template_text=dedent(res), gateway=self.gateway, domain=self.domain, resv_id=self.resv_id
        )
        self.md_show(dedent(res), md=True)


chat = DomainDelegation
