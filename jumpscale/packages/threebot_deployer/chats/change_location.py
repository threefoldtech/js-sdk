from jumpscale.sals.marketplace import MarketPlaceAppsChatflow, deployer
from jumpscale.packages.threebot_deployer.bottle.utils import (
    generate_user_identity,
    get_threebot_zos,
    list_threebot_solutions,
    redeploy_threebot_solution,
    get_threebot_config_instance,
)
from jumpscale.sals.chatflows.chatflows import StopChatFlow
from jumpscale.packages.threebot_deployer.models.user_solutions import ThreebotState
from jumpscale.packages.threebot_deployer.models import USER_THREEBOT_FACTORY
from jumpscale.sals.chatflows.chatflows import chatflow_step
from textwrap import dedent
from jumpscale.data.nacl.jsnacl import NACL
from jumpscale.loader import j
import random


class ThreebotRedeploy(MarketPlaceAppsChatflow):
    FLIST_URL = "https://hub.grid.tf/ahmed_hanafy_1/ahmedhanafy725-js-sdk-latest.flist"
    SOLUTION_TYPE = "threebot"  # chatflow used to deploy the solution
    title = "3Bot"
    steps = [
        "choose_name",
        "enter_password",
        "choose_location",
        "choose_deployment_location",
        "new_expiration",
        "create_pool",
        "deploy",
        "initializing",
        "success",
    ]

    @chatflow_step(title="Initializing chatflow")
    def choose_name(self):
        self._init_solution()
        self.branch = "development"
        all_3bot_solutions = list_threebot_solutions(self.threebot_name)
        self.stopped_3bots = [
            threebot for threebot in all_3bot_solutions if threebot["state"] == ThreebotState.STOPPED.value
        ]
        self.stopped_names = {threebot["name"]: threebot for threebot in self.stopped_3bots}
        self.name = self.kwargs["tname"]
        self.threebot_info = self.stopped_names[self.name]
        self.pool_id = self.threebot_info["compute_pool"]
        self.query = {
            "cru": self.threebot_info["cpu"] + 1,
            "mru": self.threebot_info["memory"] / 1024 + 1,
            "sru": self.threebot_info["disk_size"] / 1024 + 0.25,
        }
        self.retry = True

    @chatflow_step(title="New Expiration")
    def new_expiration(self):
        default_time = j.data.time.utcnow().timestamp + 1209600
        self.expiration = deployer.ask_expiration(self, default_time)

    def _verify_password(self, password):
        instance = USER_THREEBOT_FACTORY.get(f"threebot_{self.threebot_info['solution_uuid']}")
        if not instance.verify_secret(password):
            return False
        zos = get_threebot_zos(instance)
        user = zos._explorer.users.get(instance.identity_tid)
        words = j.data.encryption.key_to_mnemonic(password.encode().zfill(32))
        seed = j.data.encryption.mnemonic_to_key(words)
        pubkey = NACL(seed).get_verify_key_hex()
        return pubkey == user.pubkey

    @chatflow_step(title="Password")
    def enter_password(self):
        message = "Please enter the 3Bot password."
        self.password = self.secret_ask(message, required=True, max_length=32)
        while not self._verify_password(self.password):
            error = message + f"<br><br><code>Incorrect recovery password for 3Bot name {self.name}</code>"
            self.password = self.secret_ask(error, required=True, max_length=32, md=True)

    def _ask_for_continent(self):
        self.continent = self.drop_down_choice(
            "Please select the continent you would like to deploy your 3Bot in.",
            list(self.farms_by_continent.keys()),
            required=True,
        )
        self.available_farms = self.farms_by_continent[self.continent]
        self.selected_node = None

    def _ask_for_farm(self):
        farm_name_dict = {farm.name: farm for farm in self.available_farms}
        farm_name = self.drop_down_choice(
            "Please select the farm you would like to deploy your 3Bot in.", list(farm_name_dict.keys()), required=True
        )
        self.available_farms = [farm_name_dict[farm_name]]
        self.selected_node = None

    def _ask_for_node(self):
        self.retry = False
        nodes = deployer.get_all_farms_nodes(self.available_farms, **self.query)
        node_id_dict = {node.node_id: node for node in nodes}
        node_id = self.drop_down_choice(
            "Please select the node you would like to deploy your 3Bot on.", list(node_id_dict.keys()), required=True
        )
        self.selected_node = node_id_dict[node_id]
        self.available_farms = [farm for farm in self.available_farms if farm.id == self.selected_node.farm_id]

    @chatflow_step("Reserving a new pool")
    def create_pool(self):
        owner = self.threebot_name
        threebot = get_threebot_config_instance(owner, self.threebot_info["solution_uuid"])
        zos = get_threebot_zos(threebot)
        identity = generate_user_identity(threebot, self.password, zos)
        zos = j.sals.zos.get(identity.instance_name)
        farm = random.choice(self.available_farms)
        farm_name = farm.name
        self.pool_info = deployer.create_3bot_pool(
            farm_name, self.expiration, currency=self.currency, identity_name=identity.instance_name, **self.query,
        )
        if self.pool_info.escrow_information.address.strip() == "":
            raise StopChatFlow(
                f"provisioning the pool, invalid escrow information probably caused by a misconfigured, pool creation request was {self.pool_info}"
            )
        msg, qr_code = deployer.get_qr_code_payment_info(self.pool_info)
        deployer.msg_payment_info = msg
        result = deployer.wait_pool_payment(self, self.pool_info.reservation_id, qr_code=qr_code)
        if not result:
            raise StopChatFlow(f"provisioning the pool timed out. pool_id: {self.pool_info.reservation_id}")
        self.pool_id = self.pool_info.reservation_id

    @chatflow_step(title="Deployment location policy")
    def choose_location(self):
        self._get_available_farms()
        self.farms_by_continent = deployer.group_farms_by_continent(self.available_farms)
        choices = ["Automatic", "Farm", "Specific node"]
        if self.farms_by_continent:
            choices.insert(1, "Continent")
        self.node_policy = self.single_choice(
            "Please select the deployment location policy.", choices, required=True, default="Automatic"
        )

    @chatflow_step(title="Deployment location")
    def choose_deployment_location(self):
        if self.node_policy == "Continent":
            self._ask_for_continent()
        elif self.node_policy == "Farm":
            self._ask_for_farm()
        elif self.node_policy == "Specific node":
            self._ask_for_node()

    @chatflow_step(title="Deploying", disable_previous=True)
    def deploy(self):
        self.md_show_update("Starting your 3Bot...")
        node_id = self.selected_node.node_id if self.selected_node else None
        threebot = redeploy_threebot_solution(
            self.username,
            self.threebot_info["solution_uuid"],
            self.password,
            compute_pool_id=self.pool_id,
            node_id=node_id,
            solution_info={"flist": self.FLIST_URL, "branch": self.branch},
            retry=self.retry,
            bot=self,
            prompt_retry_only=True,
        )
        self.solution_id = threebot.solution_uuid

    @chatflow_step(title="Initializing", disable_previous=True)
    def initializing(self):
        self.md_show_update("Initializing your 3Bot ...")
        self.domain = self.threebot_info["domain"]
        self.threebot_url = f"https://{self.domain}/admin"
        if not j.sals.reservation_chatflow.wait_http_test(
            self.threebot_url, timeout=600, verify=not j.config.get("TEST_CERT")
        ):
            self.stop(f"Failed to initialize 3Bot on {self.threebot_url} , please contact support")
        self.domain = f"{self.domain}/admin"

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        display_name = self.threebot_info["name"]
        message = f"""\
        # Your 3Bot instance {display_name} has started
        <br />\n
        - You can access it via the browser using: <a href="https://{self.domain}" target="_blank">https://{self.domain}</a>
        """
        self.md_show(dedent(message), md=True)


chat = ThreebotRedeploy
