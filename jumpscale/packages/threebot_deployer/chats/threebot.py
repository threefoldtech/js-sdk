import uuid
import random
from textwrap import dedent
import gevent

from jumpscale.data.nacl.jsnacl import NACL
from jumpscale.loader import j
from jumpscale.packages.threebot_deployer.bottle.utils import (
    list_threebot_solutions,
    threebot_identity_context,
)
from jumpscale.packages.threebot_deployer.models import (
    BACKUP_MODEL_FACTORY,
    USER_THREEBOT_FACTORY,
)
from jumpscale.packages.threebot_deployer.models.user_solutions import ThreebotState
from jumpscale.sals.chatflows.chatflows import StopChatFlow, chatflow_step
from jumpscale.sals.marketplace import MarketPlaceAppsChatflow, deployer
from jumpscale.sals.reservation_chatflow import DeploymentFailed, deployment_context
from collections import defaultdict

FLAVORS = {
    "Silver": {"cru": 1, "mru": 2, "sru": 2},
    "Gold": {"cru": 2, "mru": 4, "sru": 4},
    "Platinum": {"cru": 4, "mru": 8, "sru": 8},
}


class ThreebotDeploy(MarketPlaceAppsChatflow):
    FLIST_URL = defaultdict(lambda: "https://hub.grid.tf/ahmed_hanafy_1/ahmedhanafy725-js-sdk-latest.flist")
    FLIST_URL["master"] = "https://hub.grid.tf/ahmed_hanafy_1/ahmedhanafy725-js-sdk-latest.flist"
    # The master flist fails for the gevent host dns resolution issue

    SOLUTION_TYPE = "threebot"  # chatflow used to deploy the solution
    title = "3Bot"
    steps = [
        "create_or_recover",
        "get_solution_name",
        "deployer_info",
        "upload_public_key",
        "set_backup_password",
        "choose_location",
        "choose_deployment_location",
        "email_settings",
        "infrastructure_setup",
        "reservation",
        "initializing",
        "new_expiration",
        "solution_extension",
        "wireguard_configs",
        "success",
    ]

    RECOVER_NAME_MESSAGE = "Please enter the 3Bot name you want to import"
    CREATE_NAME_MESSAGE = "Just like humans, each 3Bot needs their own unique identity to exist on top of the Threefold Grid. Please enter a name for your new 3Bot. This name will be used as the web address that could give you access to your 3Bot anytime."

    def _threebot_start(self):
        self._validate_user()
        self.branch = "development"
        self.solution_id = uuid.uuid4().hex
        self.username = self.user_info()["username"]
        self.threebot_name = j.data.text.removesuffix(self.username, ".3bot")
        self.explorer = j.core.identity.me.explorer
        self.solution_metadata = {}
        self.solution_metadata["owner"] = self.username
        # the main container + the nginx container with 0.25 GB disk
        self.query = {"cru": 2, "mru": 2, "sru": 2.25}
        self.container_resources = {"cru": 1, "mru": 1, "sru": 2}
        self.expiration = 60 * 60  # 60 minutes for 3bot
        self.ip_version = "IPv6"
        self.retries = 3
        self.allow_custom_domain = False
        self.custom_domain = False
        self.currency = "TFT"
        self.identity_name = j.core.identity.me.instance_name

    def _create_identities(self):
        instance_name = self.solution_name
        threebot_name = self.threebot_name
        tname = f"{threebot_name}_{instance_name}"
        email = f"{tname}@threefold.me"
        words = j.data.encryption.key_to_mnemonic(self.backup_password.encode().zfill(32))
        self.mainnet_identity_name = f"{tname}_main"
        self.testnet_identity_name = f"{tname}_test"
        if "testnet" in j.core.identity.me.explorer_url:
            self.identity_name = self.testnet_identity_name
        else:
            self.identity_name = self.mainnet_identity_name
        try:
            identity_main = j.core.identity.get(
                self.mainnet_identity_name,
                tname=tname,
                email=email,
                words=words,
                explorer_url="https://explorer.grid.tf/api/v1",
            )
            identity_test = j.core.identity.get(
                self.testnet_identity_name,
                tname=tname,
                email=email,
                words=words,
                explorer_url="https://explorer.testnet.grid.tf/api/v1",
            )
            identities = [identity_main, identity_test]
            for identity in identities:
                tname = identity.tname
                identity.admins.append(f"{threebot_name}.3bot")
                identity.register()
                identity.save()
                if identity.instance_name != self.identity_name:
                    j.core.identity.delete(identity.instance_name)

        except:
            raise StopChatFlow(
                f"Couldn't register new identites with the given name {tname}. Make sure you entered the correct password."
            )

    def _get_pool(self):
        self._get_available_farms(only_one=False, identity_name=self.identity_name)
        self._select_farms()
        self._select_pool_node()
        self.pool_info = deployer.create_3bot_pool(
            self.farm_name, self.expiration, currency=self.currency, identity_name=self.identity_name, **self.query,
        )
        if self.pool_info.escrow_information.address.strip() == "":
            raise StopChatFlow(
                f"provisioning the pool, invalid escrow information probably caused by a misconfigured, pool creation request was {self.pool_info}"
            )
        payment_info = deployer.pay_for_pool(self.pool_info)
        result = deployer.wait_demo_payment(self, self.pool_info.reservation_id)
        if not result:
            raise StopChatFlow(f"provisioning the pool timed out. pool_id: {self.pool_info.reservation_id}")
        self.md_show_update(
            f"Capacity pool {self.pool_info.reservation_id} created and funded with {payment_info['total_amount_dec']} TFT"
        )
        gevent.sleep(2)
        self.wgcfg = deployer.init_new_user_network(
            self,
            self.identity_name,
            self.pool_info.reservation_id,
            identity_name=self.identity_name,
            network_name="management",
        )
        self.md_show_update("Management network created.")
        self.pool_id = self.pool_info.reservation_id
        self.network_view = deployer.get_network_view("management", identity_name=self.identity_name)

    @chatflow_step(title="Welcome")
    def create_or_recover(self):
        self.recovery_network_name = "testnet" if "test" not in j.core.identity.me.explorer_url else "mainnet"
        self.action = self.single_choice(
            f"Would you like to create a new 3Bot instance, or import one from {self.recovery_network_name}?",
            ["Create", "Import"],
            required=True,
        )

    @chatflow_step(title="3Bot Name")
    def get_solution_name(self):
        self._threebot_start()
        valid = False
        name_message = self.RECOVER_NAME_MESSAGE if self.action == "Import" else self.CREATE_NAME_MESSAGE
        while not valid:
            self.solution_name = self.string_ask(name_message, required=True, field="name", is_identifier=True)
            threebot_solutions = list_threebot_solutions(self.solution_metadata["owner"])
            valid = True
            for sol in threebot_solutions:
                if sol["name"] == self.solution_name:
                    valid = False
                    self.md_show("The specified 3Bot name already exists. please choose another name.")
                    break
                valid = True
            if valid and self.action == "Create" and self._existing_3bot():
                valid = False
                self.md_show(
                    f"The specified 3Bot name was deployed before on {self.recovery_network_name}. Please go to the previous step and choose import or enter a new name."
                )

            if valid and self.action == "Import" and not self._existing_3bot():
                valid = False
                self.md_show("The specified 3Bot name doesn't exist.")
        self.backup_model = BACKUP_MODEL_FACTORY.get(f"{self.solution_name}_{self.threebot_name}")

    @chatflow_step(title="Deployer Information")
    def deployer_info(self):
        self.user_email = self.user_info()["email"]
        self._choose_flavor(FLAVORS)
        self.vol_size = self.flavor_resources["sru"]
        self.container_resources = self.flavor_resources

    @chatflow_step(title="SSH key (Optional)")
    def upload_public_key(self):
        self.public_key = (
            self.upload_file(
                "Please upload your public ssh key, this will allow you to access your threebot container using ssh"
            )
            or ""
        )
        self.public_key = self.public_key.strip()

    def _existing_3bot(self):
        try:
            name = f"{self.threebot_name}_{self.solution_name}"
            self.explorer.users.get(name=name)
            return True
        except j.exceptions.NotFound:
            return False

    def _verify_password(self, password):
        name = f"{self.threebot_name}_{self.solution_name}"
        user = self.explorer.users.get(name=name)
        words = j.data.encryption.key_to_mnemonic(password.encode().zfill(32))
        seed = j.data.encryption.mnemonic_to_key(words)
        pubkey = NACL(seed).get_verify_key_hex()
        return pubkey == user.pubkey

    def _select_node(self):
        if self.node_policy != "Specific node":
            return super()._select_node()

    def _select_pool_node(self):
        if self.node_policy == "Specific node":
            self.pool_node_id = self.selected_node
        else:
            super()._select_pool_node()

    def _select_farm(self):
        if self.node_policy == "Automatic":
            super()._select_farms()
        else:
            self.farm_name = random.choice(self.available_farms).name
            self.pool_farm_name = self.farm_name

    @chatflow_step(title="Deployment location policy")
    def choose_location(self):
        self._get_available_farms()
        self.farms_by_continent = deployer.group_farms_by_continent(self.available_farms)
        choices = ["Automatic", "Farm", "Specific node"]
        if self.farms_by_continent:
            choices.insert(1, "Continent")
        self.node_policy = self.single_choice(
            "Please select the deployment location policy.", choices, required=True, default="Automatic",
        )

    def _ask_for_continent(self):
        self.continent = self.drop_down_choice(
            "Please select the continent you would like to deploy your 3Bot in.",
            list(self.farms_by_continent.keys()),
            required=True,
        )
        self.available_farms = self.farms_by_continent[self.continent]

    def _ask_for_farm(self):
        farm_name_dict = {farm.name: farm for farm in self.available_farms}
        farm_name = self.drop_down_choice(
            "Please select the farm you would like to deploy your 3Bot in.", list(farm_name_dict.keys()), required=True,
        )
        self.available_farms = [farm_name_dict[farm_name]]

    def _ask_for_node(self):
        nodes = deployer.get_all_farms_nodes(self.available_farms, **self.query)
        node_id_dict = {node.node_id: node for node in nodes}
        node_id = self.drop_down_choice(
            "Please select the node you would like to deploy your 3Bot on.", list(node_id_dict.keys()), required=True,
        )
        self.selected_node = node_id_dict[node_id]
        self.available_farms = [farm for farm in self.available_farms if farm.id == self.selected_node.farm_id]
        self.retries = 1

    @chatflow_step(title="Deployment location")
    def choose_deployment_location(self):
        if self.node_policy == "Continent":
            self._ask_for_continent()
        elif self.node_policy == "Farm":
            self._ask_for_farm()
        elif self.node_policy == "Specific node":
            self._ask_for_node()
        self._create_identities()
        self.md_show_update("User identity created.")
        gevent.sleep(3)

    @chatflow_step(title="Recovery Password")
    def set_backup_password(self):
        message = (
            "Please enter the recovery password"
            if self.action == "Import"
            else "Please create a secure password for your new 3Bot. This password is used to recover your hosted 3Bot."
        )
        self.backup_password = self.secret_ask(message, required=True, max_length=32)
        while self.action == "Import" and not self._verify_password(self.backup_password):
            error = message + f"<br><br><code>Incorrect recovery password for 3Bot name {self.solution_name}</code>"
            self.backup_password = self.secret_ask(error, required=True, max_length=32, md=True)

    @chatflow_step(title="Email settings (Optional)")
    def email_settings(self):
        form = self.new_form()
        email_host_user = form.string_ask("E-mail address for your solution")
        email_host = form.string_ask("SMTP host example: `smtp.gmail.com`", default="smtp.gmail.com", md=True)
        email_host_password = form.secret_ask("Host e-mail password")

        escalation_mail_address = form.string_ask("Email address to receive email notifications on")

        form.ask("Please fill in these email configuration settings if you want to receive notifications on")
        self.email_host_user = email_host_user.value or ""
        self.email_host = email_host.value or ""
        self.email_host_password = email_host_password.value or ""
        self.escalation_mail_address = escalation_mail_address.value or ""

    @chatflow_step(title="Select your preferred payment currency")
    def payment_currency(self):
        self.currency = self.single_choice(
            "Please select the currency you would like to pay your 3Bot deployment with.",
            ["FreeTFT", "TFT", "TFTA"],
            required=True,
        )

    @chatflow_step(title="Reservation", disable_previous=True)
    def reservation(self):
        with threebot_identity_context(self.identity_name):
            super().reservation()

    @deployment_context()
    def _deploy(self):
        # 1- add node to network
        metadata = {"form_info": {"Solution name": self.solution_name, "chatflow": "threebot"}}
        self.solution_metadata.update(metadata)
        self.workload_ids = []
        deploying_message = f"""\
        # Deploying your 3Bot...\n\n
        <br>It will usually take a few minutes to succeed. Please wait patiently.\n
        You will be automatically redirected to the next step once succeeded.
        """
        self.md_show_update(dedent(deploying_message), md=True)

        # 2- reserve subdomain
        if not self.custom_domain:
            self.workload_ids.append(
                deployer.create_subdomain(
                    pool_id=self.gateway_pool.pool_id,
                    gateway_id=self.gateway.node_id,
                    subdomain=self.domain,
                    addresses=self.addresses,
                    solution_uuid=self.solution_id,
                    identity_name=self.identity_name,
                    **self.solution_metadata,
                )
            )

            success = deployer.wait_workload(self.workload_ids[-1], identity_name=self.identity_name)
            if not success:
                raise DeploymentFailed(
                    f"Failed to create subdomain {self.domain} on gateway {self.gateway.node_id} {self.workload_ids[-1]}. The resources you paid for will be re-used in your upcoming deployments.",
                    wid=self.workload_ids[-1],
                    identity_name=self.identity_name,
                )
        test_cert = j.config.get("TEST_CERT")

        # Generate a one-time token to create a user for backup
        backup_token = str(j.data.idgenerator.idgenerator.uuid.uuid4())
        self.backup_model.token = backup_token
        self.backup_model.tname = self.solution_metadata["owner"]
        self.backup_model.save()
        # 3- deploy threebot container
        environment_vars = {
            "SDK_VERSION": self.branch,
            "INSTANCE_NAME": self.solution_name,
            "THREEBOT_NAME": self.threebot_name,
            "DOMAIN": self.domain,
            "SSHKEY": self.public_key,
            "TEST_CERT": "true" if test_cert else "false",
            "MARKETPLACE_URL": f"https://{j.sals.nginx.main.websites.threebot_deployer_threebot_deployer_root_proxy_443.domain}/",
            "DEFAULT_IDENTITY": "test" if "test" in j.core.identity.me.explorer_url else "main",
            # email settings
            "EMAIL_HOST": self.email_host,
            "EMAIL_HOST_USER": self.email_host_user,
            "ESCALATION_MAIL": self.escalation_mail_address,
        }
        self.network_view = self.network_view.copy()

        ## Container logs
        log_config = j.core.config.get("LOGGING_SINK", {})
        if log_config:
            log_config["channel_name"] = f"{self.threebot_name}-{self.SOLUTION_TYPE}-{self.solution_name}".lower()

        self.workload_ids.append(
            deployer.deploy_container(
                pool_id=self.pool_id,
                node_id=self.selected_node.node_id,
                network_name=self.network_view.name,
                ip_address=self.ip_address,
                flist=self.FLIST_URL[self.branch],
                env=environment_vars,
                cpu=self.container_resources["cru"],
                memory=self.container_resources["mru"] * 1024,
                disk_size=self.container_resources["sru"] * 1024,
                secret_env={
                    "BACKUP_PASSWORD": self.backup_password,
                    "BACKUP_TOKEN": backup_token,
                    "EMAIL_HOST_PASSWORD": self.email_host_password,
                },
                interactive=False,
                log_config=log_config,
                solution_uuid=self.solution_id,
                identity_name=self.identity_name,
                **self.solution_metadata,
            )
        )
        success = deployer.wait_workload(self.workload_ids[-1], identity_name=self.identity_name)
        if not success:
            raise DeploymentFailed(
                f"Failed to create container on node {self.selected_node.node_id} {self.workload_ids[-1]}. The resources you paid for will be re-used in your upcoming deployments.",
                solution_uuid=self.solution_id,
                wid=self.workload_ids[-1],
                identity_name=self.identity_name,
            )

        # 4- expose threebot container
        wid, proxy_id = deployer.expose_address(
            pool_id=self.pool_id,
            gateway_id=self.gateway.node_id,
            network_name=self.network_view.name,
            local_ip=self.ip_address,
            port=80,
            tls_port=443,
            trc_secret=self.secret,
            node_id=self.selected_node.node_id,
            reserve_proxy=True,
            domain_name=self.domain,
            proxy_pool_id=self.gateway_pool.pool_id,
            solution_uuid=self.solution_id,
            log_config=self.trc_log_config,
            identity_name=self.identity_name,
            **self.solution_metadata,
        )
        self.workload_ids.append(wid)
        self.workload_ids.append(proxy_id)
        success = deployer.wait_workload(self.workload_ids[-1], identity_name=self.identity_name)
        if not success:
            raise DeploymentFailed(
                f"Failed to create TRC container on node {self.selected_node.node_id} {self.workload_ids[-1]}. The resources you paid for will be re-used in your upcoming deployments.",
                solution_uuid=self.solution_id,
                wid=self.workload_ids[-1],
                identity_name=self.identity_name,
            )
        self.threebot_url = f"https://{self.domain}/admin"

        instance_name = f"threebot_{self.solution_id}"
        user_threebot = USER_THREEBOT_FACTORY.get(instance_name)
        user_threebot.solution_uuid = self.solution_id
        user_threebot.identity_tid = j.core.identity.get(self.identity_name).tid
        user_threebot.name = self.solution_name
        user_threebot.owner_tname = self.threebot_name
        user_threebot.farm_name = self.farm_name
        user_threebot.state = ThreebotState.RUNNING
        if hasattr(self, "continent"):
            user_threebot.continent = self.continent
        if not self.custom_domain:
            user_threebot.subdomain_wid = self.workload_ids[-4]
        user_threebot.threebot_container_wid = self.workload_ids[-3]
        user_threebot.trc_container_wid = self.workload_ids[-2]
        user_threebot.reverse_proxy_wid = self.workload_ids[-1]
        user_threebot.explorer_url = j.core.identity.get(self.identity_name).explorer_url
        user_threebot.hash_secret(self.backup_password)
        user_threebot.save()

    @chatflow_step(title="Initializing", disable_previous=True)
    def initializing(self):
        self.md_show_update("Initializing your 3Bot ...")
        if not j.sals.reservation_chatflow.wait_http_test(
            self.threebot_url, timeout=600, verify=not j.config.get("TEST_CERT")
        ):
            self.stop(f"Failed to initialize 3Bot on {self.threebot_url} , please contact support")
        self.domain = f"{self.domain}/admin"

    @chatflow_step(title="Container Access")
    def wireguard_configs(self):
        filename = self.solution_metadata["owner"].replace(".3bot", "")
        wg_file_path = j.sals.fs.join_paths(j.core.dirs.CFGDIR, f"{filename}.3bot_apps.conf")
        wg_file_path_alt = j.sals.fs.join_paths(j.core.dirs.CFGDIR, "wireguard", f"{filename}.3bot_apps.conf")
        if j.sals.fs.exists(wg_file_path):
            content = j.sals.fs.read_file(wg_file_path)
        elif j.sals.fs.exists(wg_file_path_alt):
            content = j.sals.fs.read_file(wg_file_path_alt)
        elif hasattr(self, "wgcfg"):
            content = self.wgcfg
        else:
            config = deployer.add_access(
                self.network_view.name,
                self.network_view,
                self.selected_node.node_id,
                self.pool_id,
                bot=self,
                **self.solution_metadata,
            )
            content = config["wg"]

        msg = f"""\
        <h3> Use the following template to configure your wireguard connection. This will give you access to your network. </h3>
        <h3> Make sure you have <a target="_blank" href="https://www.wireguard.com/install/">wireguard</a> installed </h3>
        <br /><br />
        <p>{content.replace(chr(10), "<br />")}</p>
        <br /><br />
        <h3>In order to have the network active and accessible from your local/container machine, navigate to where the config is downloaded and start your connection using `wg-quick up &lt;your_download_dir&gt;/apps.conf`</h3>
        """
        self.download_file(msg=dedent(msg), data=content, filename="apps.conf", html=True)

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        display_name = self.solution_name.replace(f"{self.solution_metadata['owner']}-", "")
        message = f"""\
        # You deployed a new instance {display_name} of {self.SOLUTION_TYPE}
        <br />\n
        - You can access it via the browser using: <a href="https://{self.domain}" target="_blank">https://{self.domain}</a>

        - You can access your 3Bot via IP: `{self.ip_address}`. To use it make sure wireguard is up and running.
        """
        self.md_show(dedent(message), md=True)


chat = ThreebotDeploy
