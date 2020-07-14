import requests

from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step
from jumpscale.sals.reservation_chatflow.models import SolutionType


class FourToSixGateway(GedisChatBot):
    """
    """

    steps = ["gateway_start", "expiration_time", "wireguard_public_get", "wg_reservation", "wg_config"]
    title = "4to6 GW"

    @chatflow_step(title="Gateway")
    def gateway_start(self):
        self.user_form_data = {}
        user_info = self.user_info()
        j.sals.reservation_chatflow.validate_user(user_info)

        self.gateway = j.sals.reservation_chatflow.select_gateway(self)
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

    @chatflow_step(title="Wireguard public key")
    def wireguard_public_get(self):
        self.publickey = self.string_ask(
            "Please enter wireguard public key or leave empty if you want us to generate one for you."
        )
        self.privatekey = "enter private key here"
        res = "# Click next to continue with wireguard related deployment. Once you proceed you will not be able to go back to this step"
        self.md_show(res, md=True)

    @chatflow_step(title="Create your Wireguard ", disable_previous=True)
    def wg_reservation(self):
        if not self.publickey:
            self.privatekey, self.publickey = j.tools.wireguard.generate_key_pair()
            self.privatekey, self.publickey = self.privatekey.decode(), self.publickey.decode()

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
                "Please choose a currency that will be used for the payment", currencies, default="TFT", required=True
            )
        else:
            currency = currencies[0]

        reservation = j.sals.zos.reservation_create()
        j.sals.zos._gateway.gateway_4to6(reservation=reservation, node_id=self.gateway_id, public_key=self.publickey)

        self.resv_id = j.sals.reservation_chatflow.register_and_pay_reservation(
            reservation, self.expiration, customer_tid=j.core.identity.me.tid, currency=currency, bot=self
        )
        self.reservation_result = j.sals.reservation_chatflow.wait_reservation(self, self.resv_id)

        j.sals.reservation_chatflow.save_reservation(
            self.resv_id, f"4to6GW:{self.resv_id}", SolutionType.FourToSixGw, self.user_form_data
        )

        res = """
# Use the following template to configure your wireguard connection. This will give you access to your network.
## Make sure you have <a target="_blank" href="https://www.wireguard.com/install/">wireguard</a> installed
Click next
to download your configuration
                """
        self.md_show(res)

    @chatflow_step(title="Wireguard configuration", disable_previous=True, final_step=True)
    def wg_config(self):
        cfg = j.data.serializers.json.loads(self.reservation_result[0].data_json)
        wgconfigtemplate = """\
[Interface]
Address = {{cfg.ips[0]}}
PrivateKey = {{privatekey}}
{% for peer in cfg.peers %}
[Peer]
PublicKey = {{peer.public_key}}
AllowedIPs = {{",".join(peer.allowed_ips)}}
{% if peer.endpoint -%}
Endpoint = {{peer.endpoint}}
{% endif %}
{% endfor %}
        """
        config = j.tools.jinja2.render_template(template_text=wgconfigtemplate, cfg=cfg, privatekey=self.privatekey)

        filename = "wg-{}.conf".format(self.resv_id)
        self.download_file(msg=f"<pre>{config}</pre>", data=config, filename=filename, html=True)
        res = f"""
# In order to connect to the 4 to 6 gateway execute this command:
## ```wg-quick up ./{filename}```
                """
        self.md_show(res)


chat = FourToSixGateway
