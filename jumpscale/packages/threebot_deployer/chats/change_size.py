from jumpscale.sals.marketplace import MarketPlaceAppsChatflow, deployer
from jumpscale.packages.threebot_deployer.bottle.utils import (
    list_threebot_solutions,
    redeploy_threebot_solution,
    get_threebot_zos,
)
from jumpscale.packages.threebot_deployer.models.user_solutions import ThreebotState
from jumpscale.packages.threebot_deployer.models import USER_THREEBOT_FACTORY
from jumpscale.sals.chatflows.chatflows import chatflow_step
from textwrap import dedent
from jumpscale.data.nacl.jsnacl import NACL
from jumpscale.loader import j


FLAVORS = {
    "Silver": {"cru": 1, "mru": 2, "sru": 4},
    "Gold": {"cru": 2, "mru": 4, "sru": 4},
    "Platinum": {"cru": 4, "mru": 8, "sru": 8},
}


class ThreebotRedeploy(MarketPlaceAppsChatflow):
    FLIST_URL = "https://hub.grid.tf/ahmed_hanafy_1/ahmedhanafy725-js-sdk-latest_trc.flist"
    SOLUTION_TYPE = "threebot"  # chatflow used to deploy the solution
    title = "3Bot"
    steps = [
        "choose_name",
        "enter_password",
        "choose_flavor",
        "deploy",
        "initializing",
        "new_expiration",
        "solution_extension",
        "success",
    ]

    @chatflow_step(title="Initializing chatflow")
    def choose_name(self):
        self.expiration = 10 * 60  # 10 minutes for 3bot
        self.retry = True
        self._init_solution()
        all_3bot_solutions = list_threebot_solutions(self.threebot_name)
        self.stoped_3bots = [
            threebot for threebot in all_3bot_solutions if threebot["state"] == ThreebotState.STOPPED.value
        ]
        self.stopped_names = {threebot["name"]: threebot for threebot in self.stoped_3bots}
        self.name = self.kwargs["tname"]
        self.threebot_info = self.stopped_names[self.name]
        self.pool_id = self.threebot_info["compute_pool"]

    @chatflow_step(title="Choose size")
    def choose_flavor(self):
        self._choose_flavor(FLAVORS)
        self.query = self.flavor_resources
        self.cpu = self.query["cru"]
        self.memory = self.query["mru"] * 1024
        self.disk_size = self.query["sru"] * 1024

    @chatflow_step(title="New Expiration")
    def new_expiration(self):
        self.pool = j.sals.zos.get().pools.get(self.pool_id)
        cloud_units = deployer._calculate_cloud_units(**self.query)
        cu, su = cloud_units.cu, cloud_units.su
        # guard in case of extending of 0 will raise zero division
        if not cu:
            cu = 1
        if not su:
            expiration_time = self.pool.cus / cu
        else:
            expiration_time = min(self.pool.cus / cu, self.pool.sus / su)
        if expiration_time < 60 * 60:
            default_time = j.data.time.utcnow().timestamp + 1209600
            self.expiration = deployer.ask_expiration(
                self, default_time, pool_empty_at=j.data.time.utcnow().timestamp + expiration_time
            )
        else:
            self.expiration = 0

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

    @chatflow_step(title="Deploying", disable_previous=True)
    def deploy(self):
        self.md_show_update("Starting your 3Bot...")
        solution_info = {
            "cpu": self.cpu,
            "memory": self.memory,
            "disk_size": self.disk_size,
            "flist": self.FLIST_URL,
            "branch": self.branch,
        }
        threebot = redeploy_threebot_solution(
            self.username,
            self.threebot_info["solution_uuid"],
            self.password,
            solution_info=solution_info,
            retry=True,
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
