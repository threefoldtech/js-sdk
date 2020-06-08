from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.god import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step, StopChatFlow
from jumpscale.sals.reservation_chatflow.models import SolutionType
import time


class NetworkDeploy(GedisChatBot):
    steps = ["network_reservation", "network_info"]
    
    @chatflow_step(title="Deploy Network")
    def network_reservation(self):
        user_form_data = {}
        user_info = self.user_info()
        # j.sals.reservation_chatflow.validate_user(user_info)
        user_form_data["chatflow"] = "network"
        network_name = self.string_ask("Please enter a network name", required=True, field="name")
        user_form_data["Currency"] = self.single_choice(
            "Please choose a currency that will be used for the payment", ["FreeTFT", "TFT"], default="TFT", required=True
        )
        expiration = self.datetime_picker(
            "Please enter network expiration time.",
            required=True,
            min_time=[3600, "Date/time should be at least 1 hour from now"],
            default=j.data.time.utcnow().timestamp + 3900,
        )

        ips = ["IPv6", "IPv4"]
        ipversion = self.single_choice(
            "How would you like to connect to your network? IPv4 or IPv6? If unsure, choose IPv4",
            ips, required=True
        )
        user_form_data["Solution expiration"] = j.data.time.get(expiration).humanize()

        reservation = j.sals.zos.reservation_create()
        ip_range = j.sals.reservation_chatflow.get_ip_range(self)
        res = j.sals.reservation_chatflow.get_solution_metadata(network_name, SolutionType.Network, user_form_data)
        reservation = j.sals.reservation_chatflow.add_reservation_metadata(reservation, res)
        
        while True:
            self.config = j.sals.reservation_chatflow.create_network(
                network_name,
                reservation,
                ip_range,
                j.core.identity.tid,
                ipversion,
                expiration=expiration,
                currency=user_form_data["Currency"],
                bot=self,
            )
            try:
                j.sals.reservation_chatflow.register_and_pay_reservation(self.config["reservation_create"], bot=self)
                break
            except StopChatFlow as e:
                if "wireguard listen port already in use" in e.msg:
                    j.sals.zos.reservation_cancel(self.config["rid"])
                    time.sleep(5)
                    continue
                raise

    @chatflow_step(title="Network Information", disable_previous=True)
    def network_info(self):
        print(self.config)
        message = """
### Use the following template to configure your wireguard connection. This will give you access to your network.
#### Make sure you have <a target="_blank" href="https://www.wireguard.com/install/">wireguard</a> installed
Click next
to download your configuration
        """
        
        self.md_show(message, md=True, html=True)

        filename = "wg-{}.conf".format(self.config["rid"])
        self.download_file(msg=f'<pre>{self.config["wg"]}</pre>', data=self.config["wg"], filename=filename, html=True)

        message = f"""
### In order to have the network active and accessible from your local/container machine. To do this, execute this command:
#### ```wg-quick up /etc/wireguard/{filename}```
# Click next
        """

        self.md_show(message, md=True)


chat = NetworkDeploy
