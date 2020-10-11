import uuid
from textwrap import dedent

from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.reservation_chatflow import deployer


class FourToSixGateway(GedisChatBot):
    steps = ["gateway_start", "wireguard_public_get", "wg_reservation", "success"]
    title = "4to6 GW"

    @chatflow_step(title="Gateway")
    def gateway_start(self):
        deployer.chatflow_pools_check()
        self.solution_id = uuid.uuid4().hex
        self.solution_metadata = {}
        self.gateway, pool = deployer.select_gateway(bot=self)
        self.pool_id = pool.pool_id
        self.gateway_id = self.gateway.node_id

    @chatflow_step(title="Wireguard public key")
    def wireguard_public_get(self):
        self.publickey = self.string_ask(
            "Please enter wireguard public key or leave empty if you want us to generate one for you."
        )
        self.privatekey = "enter private key here"
        res = "### Click next to continue with wireguard related deployment. Once you proceed you will not be able to go back to this step"
        self.md_show(res, md=True)

    @chatflow_step(title="Create your Wireguard ", disable_previous=True)
    def wg_reservation(self):
        if not self.publickey:
            self.privatekey, self.publickey = j.tools.wireguard.generate_key_pair()
            self.privatekey = self.privatekey.decode()

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
        self.reservation_result = j.sals.zos.get().workloads.get(self.resv_id).info.result

    @chatflow_step(title="Wireguard Configuration", disable_previous=True, final_step=True)
    def success(self):
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
        self.wgconf = j.tools.jinja2.render_template(
            template_text=dedent(wgconfigtemplate), cfg=cfg, privatekey=self.privatekey
        )
        self.filename = "wg-{}.conf".format(self.resv_id)

        msg = f"""\
        <h3> Use the following template to configure your wireguard connection. This will give you access to your network. </h3>
        <h3> Make sure you have <a target="_blank" href="https://www.wireguard.com/install/">wireguard</a> installed </h3>
        <br />
        <p style="text-align:center">{self.wgconf.replace(chr(10), "<br />")}</p>
        <br />
        <h3>In order to have the network active and accessible from your local/container machine, navigate to where the config is downloaded and start your connection using `wg-quick up &lt;your_download_dir&gt;/{self.filename}`</h3>
        """
        self.download_file(msg=dedent(msg), data=self.wgconf, filename=self.filename, html=True)


chat = FourToSixGateway
