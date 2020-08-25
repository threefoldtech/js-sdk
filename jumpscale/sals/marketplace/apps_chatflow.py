import uuid
import random

import requests

from jumpscale.core.base import StoredFactory
from jumpscale.loader import j
from .solutions import solutions
from .deployer import deployer
from .chatflow import MarketPlaceChatflow
from jumpscale.packages.marketplace.bottle.models import UserEntry
from jumpscale.sals.chatflows.chatflows import StopChatFlow, chatflow_step
from jumpscale.core.base import Base, fields

FARM_NAMES = ["freefarm"]
# For fees stuff
EXPLORER_URL = j.core.identity.me.explorer_url
SERVICE_FEES = 5
NETWORK = "TEST" if "testnet" in EXPLORER_URL or "devnet" in EXPLORER_URL else "STD"
WALLET_NAME = f"appstore_wallet_{NETWORK.lower()}"

MARKETPLACE_URL ="https://staging.marketplace.threefold.me/"
CREATE_USER_ENDPOINT = "marketplace/actors/backup/init"
PUBLIC_KEY_ENDPOINT = "marketplace/actors/backup/public_key"

class MarketPlaceAppsChatflow(MarketPlaceChatflow):
    def __init__(self, service_fees=0, backup_fees=0, backup_enabled=False, backup_config=None, *args, **kwargs):
        self.service_fees = service_fees
        self.backup_fees = backup_fees
        self.backup_enabled = backup_enabled
        self.backup_config = {} or backup_config

    def _init_solution(self):
        self._validate_user()
        self.solution_id = uuid.uuid4().hex
        self.solution_metadata = {}
        self.solution_metadata["owner"] = self.user_info()["username"]
        self.threebot_name = j.data.text.removesuffix(self.user_info()["username"], ".3bot")
        self.query = dict()

    @property
    def appstore_wallet(self):
        if WALLET_NAME in j.clients.stellar.list_all():
            return j.clients.stellar.get(WALLET_NAME)
        else:
            wallet = j.clients.stellar.get(WALLET_NAME)
            wallet.network = NETWORK
            if NETWORK == "TEST":
                wallet.activate_through_friendbot()
            else:
                wallet.activate_through_threefold_service()
            wallet.add_known_trustline("TFT")
            wallet.add_known_trustline("FreeTFT")
            wallet.add_known_trustline("TFTA")
            wallet.save()
            return wallet

    def _refund(self, transaction, effects):
        currency = self.currency or "TFT"
        if effects.amount < 0:
            return False

        if effects.asset_code != (currency):
            return False

        refund_address = self.appstore_wallet.get_sender_wallet_address(transaction.hash)
        asset = self.appstore_wallet.get_asset(currency)

        amount = effects.amount
        if currency == "TFT":
            amount = effects.amount - 0.1  # Transaction fees
        self.appstore_wallet.transfer(
            refund_address, amount, asset=f"{asset.code}:{asset.issuer}", fund_transaction=False
        )
        return True

    def _pay(self, msg=""):
        currency = self.currency or "TFT"
        self.memo_text = j.data.idgenerator.chars(15)
        payment_info_content = j.sals.zos._escrow_to_qrcode(
            escrow_address=self.appstore_wallet.address,
            escrow_asset=currency,
            total_amount=SERVICE_FEES,
            message=self.memo_text,
        )

        message_text = f"""{msg}
<h3> Please proceed with paying the fees for this service</h3>
Scan the QR code with your application (do not change the message) or enter the information below manually and proceed with the payment.
Make sure to add the payment ID as memo_text
Please make the transaction and press Next
<h4> Wallet address: </h4>  {self.appstore_wallet.address} \n
<h4> Amount: </h4>  {SERVICE_FEES} {currency}\n
<h4> Message (Payment ID): </h4>  {self.memo_text} \n
        """

        start_epoch = j.data.time.get().timestamp
        expiration_epoch = j.data.time.get(start_epoch + (10 * 60)).timestamp
        transfer_complete = False
        self.qrcode_show(data=payment_info_content, msg=message_text, scale=4, update=True, html=True, md=True)
        while not transfer_complete:
            if expiration_epoch < j.data.time.get().timestamp:
                self.stop("Payment not recieved in time. Please try again later.")
            time_left = j.data.time.get(expiration_epoch).humanize(granularity=["minute", "second"])
            message = f"Waiting for successful transfer of {SERVICE_FEES} {currency}. Process will be cancelled in {time_left}"
            self.md_show_update(message, md=True, html=True)
            transactions = self.appstore_wallet.list_transactions()
            for transaction in transactions:
                if not self.appstore_wallet.check_is_payment_transaction(transaction.hash):
                    continue
                transaction_effects = self.appstore_wallet.get_transaction_effects(
                    transaction.hash, address=self.appstore_wallet.address
                )[0]
                amount_transfered = float(transaction_effects.amount)
                if transaction.memo_text == self.memo_text:
                    if amount_transfered == SERVICE_FEES:
                        transfer_complete = True
                        self.md_show(
                            "You have successfully paid for using this service. Click next to continue with your deployment."
                        )
                        return
                    else:
                        if self._refund(transaction, transaction_effects):
                            msg = f"\n`Wrong amount of {currency}'s has been received, they have been sent back to your wallet. Please try again`\n\n"
                            return self._pay(msg)

    def _wgconf_show_check(self):
        if hasattr(self, "wgconf"):
            msg = f"""<h3> Use the following template to configure your wireguard connection. This will give you access to your network. </h3>
<h3> Make sure you have <a target="_blank" href="https://www.wireguard.com/install/">wireguard</a> installed </h3>
<br>
<pre style="text-align:center">{self.wgconf}</pre>
<br>
<h3>navigate to where the config is downloaded and start your connection using "wg-quick up ./apps.conf"</h3>
"""
            self.download_file(msg=msg, data=self.wgconf, filename="apps.conf", html=True)

    def _get_pool(self):
        available_farms = []
        for farm_name in FARM_NAMES:
            available, _, _, _, _ = deployer.check_farm_capacity(farm_name, currencies=[self.currency], **self.query)
            if available:
                available_farms.append(farm_name)

        self.farm_name = random.choice(available_farms)

        user_networks = solutions.list_network_solutions(self.solution_metadata["owner"])
        networks_names = [n["Name"] for n in user_networks]
        if "apps" in networks_names:
            # old user
            self.pool_info = deployer.create_solution_pool(
                bot=self,
                username=self.solution_metadata["owner"],
                farm_name=self.farm_name,
                expiration=self.expiration,
                currency=self.currency,
                **self.query,
            )
            result = deployer.wait_pool_payment(self, self.pool_info.reservation_id)
            if not result:
                raise StopChatFlow(f"Waiting for pool payment timedout. pool_id: {self.pool_info.reservation_id}")
        else:
            # new user
            self.pool_info, self.wgconf = deployer.init_new_user(
                bot=self,
                username=self.solution_metadata["owner"],
                farm_name=self.farm_name,
                expiration=self.expiration,
                currency=self.currency,
                **self.query,
            )

        if not self.pool_info:
            raise StopChatFlow(f"Failed to deploy solution {self.pool_info}")
        self.pool_id = self.pool_info.reservation_id
        return self.pool_id

    def _deploy_network(self):
        # get ip address
        self.network_view = deployer.get_network_view(f"{self.solution_metadata['owner']}_apps")
        self.ip_address = None
        while not self.ip_address:
            self.selected_node = deployer.schedule_container(self.pool_info.reservation_id)
            result = deployer.add_network_node(
                self.network_view.name,
                self.selected_node,
                self.pool_info.reservation_id,
                self.network_view,
                bot=self,
                owner=self.solution_metadata.get("owner"),
            )
            if result:
                self.md_show_update("Deploying Network on Nodes....")
                for wid in result["ids"]:
                    success = deployer.wait_workload(wid)
                    if not success:
                        raise StopChatFlow(f"Failed to add node {self.selected_node.node_id} to network {wid}")
                self.network_view = self.network_view.copy()
            self.ip_address = self.network_view.get_free_ip(self.selected_node)
        return self.ip_address

    def _get_domain(self):
        # get domain for the ip address
        self.md_show_update("Preparing gateways ...")
        gateways = deployer.list_all_gateways(self.user_info()["username"])
        if not gateways:
            raise StopChatFlow("There are no available gateways in the farms bound to your pools.")

        domains = dict()
        for gw_dict in gateways.values():
            gateway = gw_dict["gateway"]
            for domain in gateway.managed_domains:
                try:
                    if j.sals.crtsh.has_reached_limit(domain):
                        continue
                except requests.exceptions.HTTPError:
                    continue
                domains[domain] = gw_dict

        if not domains:
            raise StopChatFlow("Letsencrypt limit has been reached on all gateways")

        self.domain = random.choice(list(domains.keys()))

        self.gateway = domains[self.domain]["gateway"]
        self.gateway_pool = domains[self.domain]["pool"]

        solution_name = self.solution_name.replace(".", "").replace("_", "-")
        # check if domain name is free or append random number
        full_domain = f"{solution_name}.{self.domain}"
        while True:
            if j.tools.dnstool.is_free(full_domain):
                self.domain = full_domain
                break
            else:
                random_number = random.randint(1000, 100000)
                full_domain = f"{solution_name}-{random_number}.{self.domain}"

        self.addresses = []
        for ns in self.gateway.dns_nameserver:
            self.addresses.append(j.sals.nettools.get_host_by_name(ns))

        self.secret = f"{j.core.identity.me.tid}:{uuid.uuid4().hex}"
        return self.domain

    @chatflow_step(title="Solution Name")
    def solution_name(self):
        valid = False
        while not valid:
            self.solution_name = self.string_ask("Please enter a name for your solution", required=True)
            method = getattr(solutions, f"list_{self.SOLUTION_TYPE}_solutions")
            solutions_list = method(self.solution_metadata["owner"], sync=False)
            valid = True
            for sol in solutions_list:
                if sol["Name"] == self.solution_name:
                    valid = False
                    self.md_show("The specified solution name already exists. please choose another.")
                    break
                valid = True
        self.solution_name = f"{self.solution_metadata['owner']}-{self.solution_name}"

    @chatflow_step(title="Payment currency")
    def payment_currency(self):
        self.currency = self.single_choice(
            "Please select the currency you want to pay with.", ["FreeTFT", "TFT", "TFTA"], required=True
        )

    @chatflow_step(title="Expiration Time")
    def solution_expiration(self):
        self.expiration = deployer.ask_expiration(self)

    @chatflow_step(title="Setup")
    def infrastructure_setup(self):
        self._get_pool()
        self._deploy_network()
        self._get_domain()

    def _init_backup_repos(self, solution_name, password):
        import os
        import requests
        import nacl.encoding
        from nacl.public import Box
        headers = {"Content-Type": "application/json"}
        tname = j.core.identity.me.tname
        username = tname.split(".")[0]
        url = os.path.join(MARKETPLACE_URL, PUBLIC_KEY_ENDPOINT)
        response = requests.post(url)
        if response.status_code != 200:
            raise Exception("Can not get market place publickey")
        mrkt_pub_key = nacl.public.PublicKey(response.json().encode(), nacl.encoding.Base64Encoder)
        priv_key = j.core.identity.me.nacl.private_key
        box = Box(priv_key, mrkt_pub_key)
        password_encrypted = box.encrypt(password.encode(), encoder=nacl.encoding.Base64Encoder).decode()
        self.backup_config["password"] = password_encrypted
        data = {"threebot_name": tname, "passwd": password_encrypted, solution_name: ""}
        url = os.path.join(MARKETPLACE_URL, CREATE_USER_ENDPOINT)
        response = requests.post(url, json=data, headers=headers)
        if response.status_code != 200:
            raise j.exceptions.Value(f"can not create user with name:{username}, error={response.text}")
        return response.json()
    
    def _setup_backup_conf(self, solution_name):
        # TODO Make sure user cannot create two solutions with the same name
        password = j.data.idgenerator.chars(15)
        servers = self._init_backup_repos(solution_name, password)
        self.backup_config["servers"] = servers
        tname = j.core.identity.me.tname.split(".")[0]
        self.backup_config['username'] = f"{tname}_{solution_name}"

    @chatflow_step(title="Backup")
    def backup_choice(self):
        enable_backup = self.single_choice(
            "Do you want to enable backup for this solution?", ["Yes", "No"], required=True
        )
        self.backup_enabled = enable_backup == "Yes"

    @chatflow_step(title="Service fees")
    def pay_service_fees(self):
        self._pay()
        if self.backup_enabled:
            self._setup_backup_conf(self.solution_name)

    def _pay(self, msg=""):
        total_amount = self.service_fees
        backup_text = ""
        if self.backup_enabled:
            total_amount = self.service_fees + self.backup_fees
            backup_text = """
<h4> Backup Fees: </h4>  {BACKUP_FEES} {currency}\n
"""

        currency = self.currency or "TFT"
        self.memo_text = j.data.idgenerator.chars(15)
        payment_info_content = j.sals.zos._escrow_to_qrcode(
            escrow_address=self.appstore_wallet.address,
            escrow_asset=currency,
            total_amount=total_amount,
            message=self.memo_text,
        )

        message_text = f"""{msg}
<h3> Please proceed with paying the fees for this service</h3>
Scan the QR code with your application (do not change the message) or enter the information below manually and proceed with the payment.
Make sure to add the payment ID as memo_text
Please make the transaction and press Next
<h4> Wallet address: </h4>  {self.appstore_wallet.address} \n
<h4> Service Fees: </h4>  {self.service_fees} {currency}\n
<h4> Message (Payment ID): </h4>  {self.memo_text} \n
{backup_text}
<h4> Amount: </h4>  {total_amount} {currency}\n
"""

        start_epoch = j.data.time.get().timestamp
        expiration_epoch = j.data.time.get(start_epoch + (10 * 60)).timestamp
        transfer_complete = False
        self.qrcode_show(data=payment_info_content, msg=message_text, scale=4, update=True, html=True, md=True)
        while not transfer_complete:
            if expiration_epoch < j.data.time.get().timestamp:
                self.stop("Payment not recieved in time. Please try again later.")
            time_left = j.data.time.get(expiration_epoch).humanize(granularity=["minute", "second"])
            message = f"Waiting for successful transfer of {total_amount} {currency}. Process will be cancelled in {time_left}"
            self.md_show_update(message, md=True, html=True)
            transactions = self.appstore_wallet.list_transactions()
            for transaction in transactions:
                if not self.appstore_wallet.check_is_payment_transaction(transaction.hash):
                    continue
                transaction_effects = self.appstore_wallet.get_transaction_effects(
                    transaction.hash, address=self.appstore_wallet.address
                )[0]
                amount_transfered = float(transaction_effects.amount)
                if transaction.memo_text == self.memo_text:
                    if amount_transfered == total_amount:
                        transfer_complete = True
                        self.md_show(
                            "You have successfully paid for using this service. Click next to continue with your deployment."
                        )
                        return
                    else:
                        if self._refund(transaction, transaction_effects):
                            msg = f"\n`Wrong amount of {currency}'s has been received, they have been sent back to your wallet. Please try again`\n\n"
                            return self._pay(msg)
