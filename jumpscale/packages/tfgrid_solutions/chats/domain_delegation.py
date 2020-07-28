import requests
import uuid
from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.reservation_chatflow.models import SolutionType
from jumpscale.sals.reservation_chatflow import deployer


class DomainDelegation(GedisChatBot):
    steps = ["select_pool", "domain_name", "reservation", "success"]
    title = "Domain Delegation"

    @chatflow_step(title="Pool")
    def select_pool(self):
        self.solution_id = uuid.uuid4().hex
        self.gateway, pool = deployer.select_gateway(bot=self)
        self.pool_id = pool.pool_id

    @chatflow_step(title="Domain delegation name")
    def domain_name(self):
        self.domain = self.string_ask("Please enter a domain name to delegate", required=True)
        self.gateway_id = self.gateway.node_id

    @chatflow_step(title="Reservation")
    def reservation(self):
        metadata = {"SolutionName": self.domain, "ٍSolutionType": "domain_delegate"}
        self.resv_id = deployer.delegate_domain(
            self.pool_id, self.gateway_id, self.domain, **metadata, solution_uuid=self.solution_id
        )
        success = deployer.wait_workload(self.resv_id, self)
        if not success:
            raise StopChatFlow(f"Failed to deploy workload {self.resv_id}")

    @chatflow_step(title="Success", disable_previous=True)
    def success(self):
        res = """\
# Delegated your domain successfully

Reservation id: {{resv_id}}

Please create an `NS` record in your dns manager for domain: `{{domain}}` pointing to:
{% for dns in gateway.dns_nameserver -%}
- {{dns}}
{% endfor %}
            """
        res = j.tools.jinja2.render_template(text=res, gateway=self.gateway, domain=self.domain, resv_id=self.resv_id)
        self.md_show(res)


chat = DomainDelegation
