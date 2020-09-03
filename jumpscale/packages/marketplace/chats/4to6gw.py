import uuid

from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import StopChatFlow, chatflow_step
from jumpscale.sals.marketplace import MarketPlaceChatflow, deployer


class FourToSixGateway(MarketPlaceChatflow):
    steps = [
        "select_pool",
        "gateway_start",
        "wireguard_public_get",
        "wg_reservation",
        "wg_config",
    ]
    title = "4 to 6 Gateway"

    @chatflow_step(title="Pool")
    def select_pool(self):
        self.username = self.user_info()["username"]
        self._validate_user()
        self.solution_id = uuid.uuid4().hex
        self.solution_metadata = {"owner": self.username}

    @chatflow_step(title="Select a Gateway")
    def gateway_start(self):
        self.gateway, pool = deployer.select_gateway(self.solution_metadata["owner"], bot=self)
        self.pool_id = pool.pool_id
        self.gateway_id = self.gateway.node_id

    @chatflow_step(title="Wireguard Public Key")
    def wireguard_public_get(self):
        self.publickey = self.string_ask(
            "Please enter a Wireguard public key, or leave it blank if you want us to generate one for you."
        )
        self.privatekey = "enter private key here"
        res = "### Click 'Next' to continue with your Wireguard deployment process. Once proceeded, you will not be able to go back to this step."
        self.md_show(res, md=True)

    @chatflow_step(title="Creating Your Wireguard", disable_previous=True)
    def wg_reservation(self):
        if not self.publickey:
            self.privatekey, self.publickey = j.tools.wireguard.generate_key_pair()

        self.resv_id = deployer.create_ipv6_gateway(
            self.gateway_id,
            self.pool_id,
            self.publickey,
            SolutionType="4to6GW",
            solution_uuid=self.solution_id,
            **self.solution_metadata,
        )
        success = deployer.wait_workload(self.resv_id, self)
        if not success:
            raise StopChatFlow(f"Failed to deploy workload {self.resv_id}")
        self.reservation_result = j.sals.zos.workloads.get(self.resv_id).info.result
        res = """
## Please use the following template to configure your Wireguard connection. This will give you an access to your network.
\n<br/>\n
Make sure you have <a target="_blank" href="https://www.wireguard.com/install/">Wireguard</a> installed locally.
Click 'Next'
to download your configuration.
        """
        self.md_show(res)

    @chatflow_step(title="Wireguard Configuration", disable_previous=True)
    def wg_config(self):
        cfg = j.data.serializers.json.loads(self.reservation_result.data_json)
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
        config = j.tools.jinja2.render_template(
            template_text=wgconfigtemplate, cfg=cfg, privatekey=self.privatekey.decode()
        )
        config = config

        filename = "wg-{}.conf".format(self.resv_id)
        self.download_file(msg=f"<pre>{config}</pre>", data=config, filename=filename, html=True)
        res = f"""
# In order to connect to the 4 to 6 Gateway, please execute the command below:
\n<br/>\n
## ```wg-quick up ./{filename}```
                    """
        self.md_show(res, md=True)


chat = FourToSixGateway
