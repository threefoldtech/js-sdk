import requests

from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.reservation_chatflow.models import SolutionType


class DomainDelegation(GedisChatBot):
    steps = ["domain_delegation_name", "domain_name", "expiration_time", "domain_pay", "success"]
    title = "Domain Delegation"

    @chatflow_step(title="Domain delegation name")
    def domain_delegation_name(self):
        user_info = self.user_info()
        self.user_form_data = {}
        j.sals.reservation_chatflow.validate_user(user_info)
        self.user_form_data["chatflow"] = "delegated_domain"

    @chatflow_step(title="Domain name & Choose gateway")
    def domain_name(self):
        form = self.new_form()
        domain = form.string_ask("Please enter a domain name to delegate", required=True)
        gateways = j.sals.reservation_chatflow.list_gateways(self)
        if not gateways:
            return self.stop("No available gateway")
        options = sorted(list(gateways.keys()))
        gateway_choice = form.drop_down_choice("Please choose a gateway", options, required=True)
        form.ask()
        self.user_form_data["Domain"] = domain.value
        self.user_form_data["Solution name"] = f"{domain.value}"
        self.gateway = gateways[gateway_choice.value]
        self.gateway_id = self.gateway.node_id
        self.user_form_data["Gateway"] = self.gateway_id

    @chatflow_step(title="Expiration time")
    def expiration_time(self):
        self.expiration = self.datetime_picker(
            "Please enter solution expiration time.",
            required=True,
            min_time=[3600, "Date/time should be at least 1 hour from now"],
            default=j.data.time.get().timestamp + 3900,
        )
        self.user_form_data["Expiration"] = j.data.time.get(self.expiration).humanize()

    @chatflow_step(title="Payment", disable_previous=True)
    def domain_pay(self):
        currencies = list()
        farm_id = self.gateway.farm_id
        try:
            addresses = j.sals.zos._explorer.farms.get(farm_id).wallet_addresses
        except requests.HTTPError:
            self.stop(f"The selected gateway {self.gateway.node_id} have an invalid farm_id {farm_id}")
        for address in addresses:
            if address.asset not in currencies:
                currencies.append(address.asset)

        if len(currencies) > 1:
            currency = self.single_choice(
                "Please choose a currency that will be used for the payment", currencies, default="", required=True
            )
        else:
            currency = currencies[0]

        self.reservation = j.sals.zos.reservation_create()
        j.sals.zos._gateway.delegate_domain(
            reservation=self.reservation, node_id=self.gateway_id, domain=self.user_form_data["Domain"]
        )

        res = j.sals.reservation_chatflow.get_solution_metadata(
            self.user_form_data["Solution name"], SolutionType.DelegatedDomain, self.user_form_data
        )
        self.reservation = j.sals.reservation_chatflow.add_reservation_metadata(self.reservation, res)

        self.resv_id = j.sals.reservation_chatflow.register_and_pay_reservation(
            self.reservation, self.expiration, customer_tid=j.core.identity.me.tid, currency=currency, bot=self
        )

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        j.sals.reservation_chatflow.save_reservation(
            self.resv_id, self.user_form_data["Solution name"], SolutionType.DelegatedDomain, self.user_form_data
        )

        res = """\
# Delegated your domain successfully

Reservation id: {{reservation.id}}

Please create an `NS` record in your dns manager for domain: `{{domain}}` pointing to:
{% for dns in gateway.dns_nameserver -%}
- {{dns}}
{% endfor %}
        """
        res = j.tools.jinja2.render_template(
            template_text=res, gateway=self.gateway, domain=self.user_form_data["Domain"], reservation=self.reservation
        )
        self.md_show(res)


chat = DomainDelegation
