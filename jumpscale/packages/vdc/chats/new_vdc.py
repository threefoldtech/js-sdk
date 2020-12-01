from jumpscale.loader import j
from jumpscale.sals.vdc.size import VDCFlavor
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step


class VDCDeploy(GedisChatBot):
    title = "VDC"
    steps = ["vdc_info", "deploy", "success"]

    def _init(self):
        self.user_info_data = self.user_info()
        self.username = self.user_info_data["username"]

    def _vdc_form(self):
        vdc_names = [vdc.vdc_name for vdc in j.sals.vdc.list(self.username)]
        vdc_flavros = [flavor.name for flavor in VDCFlavor]
        form = self.new_form()
        self.vdc_name = form.string_ask(
            "Please enter a name for your solution (will be used in listing and deletions in the future and in having a unique url)",
            required=True,
            not_exist=["VDC", vdc_names],
        )
        self.vdc_secret = form.secret_ask("VDC Secret (will be used ...)", min_length=8, required=True,)
        self.vdc_flavor = form.single_choice(
            "Choose the VDC Flavor", options=vdc_flavros, default=vdc_flavros[0], required=True
        )
        form.ask()

    def _k3s_and_minio_form(self):
        form = self.new_form()
        self.cluster_secret = form.secret_ask("K3s cluster secret (will be used ...)", min_length=8, required=True,)
        self.minio_access_key = form.string_ask("Minio access key (will be used ...)", required=True,)
        self.minio_secret_key = form.secret_ask("Minio secret key (will be used ...)", min_length=8, required=True,)
        form.ask()

    @chatflow_step(title="VDC Information")
    def vdc_info(self):
        self._init()
        self._vdc_form()
        self._k3s_and_minio_form()

    @chatflow_step(title="VDC Deployment")
    def deploy(self):
        self.vdc = j.sals.vdc.new(
            vdc_name=self.vdc_name.value, owner_tname=self.username, flavor=VDCFlavor[self.vdc_flavor.value]
        )
        self.deployer = self.vdc.get_deployer(password=self.vdc_secret.value, bot=self)
        # TODO: price plan
        message = f"""\
Please fund this wallet's address with some TFTs to use in deployment:
  - ### {self.vdc.wallet.address}
        """
        self.md_show(message, md=True)

        self.md_show_update("Deploying your VDC...")
        try:
            # yaml text to download self.config
            # show IP
            self.config = self.deployer.deploy_vdc(
                cluster_secret=self.cluster_secret.value,
                minio_ak=self.minio_access_key.value,
                minio_sk=self.minio_secret_key.value,
            )
            # TODO: optional expose minio
            self.public_ip = self.vdc.kubernetes[0].public_ip
        except j.exceptions.Runtime as err:
            j.logger.error(str(err))
            StopChatFlow(str(err))

    @chatflow_step(title="VDC Deployment Success", final_step=True)
    def success(self):
        self.download_file(
            f"""
# Your VDC {self.vdc.vdc_name} has been deployed successfuly.
Please download the config file to `~/.kube/config` to start using your cluster with [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
        """,
            self.config,
            f"{self.vdc_name}.yaml",
            md=True,
        )


chat = VDCDeploy
