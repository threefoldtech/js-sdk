from jumpscale.loader import j
from jumpscale.sals.vdc.size import VDC_SIZE, INITIAL_RESERVATION_DURATION
from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step
from textwrap import dedent


class VDCDeploy(GedisChatBot):
    title = "VDC"
    steps = ["vdc_info", "deploy", "expose_s3", "success"]

    def _init(self):
        self.user_info_data = self.user_info()
        self.username = self.user_info_data["username"]

    def _vdc_form(self):
        vdc_names = [vdc.vdc_name for vdc in j.sals.vdc.list(self.username)]
        vdc_flavors = [flavor for flavor in VDC_SIZE.VDC_FLAVORS]
        vdc_flavor_messages = []
        for flavor in vdc_flavors:
            plan = VDC_SIZE.VDC_FLAVORS[flavor]
            vdc_flavor_messages.append(
                f"{flavor.name}: {plan['k8s']['size'].name} Kubernetes cluster, {plan['s3']['size'].name} S3 with {VDC_SIZE.S3_ZDB_SIZES[plan['s3']['size']]['sru']:,} GB"
            )
        form = self.new_form()
        self.vdc_name = form.string_ask(
            "Please enter a name for your VDC (will be used in listing and deletions in the future and in having a unique url)",
            required=True,
            not_exist=["VDC", vdc_names],
        )
        self.vdc_secret = form.secret_ask("VDC Secret (Secret for controlling the vdc)", min_length=8, required=True,)
        self.vdc_flavor = form.single_choice(
            "Choose the VDC Flavor", options=vdc_flavor_messages, default=vdc_flavor_messages[0], required=True,
        )
        form.ask()
        self.vdc_flavor = self.vdc_flavor.value.split(":")[0]

    def _k3s_and_minio_form(self):
        form = self.new_form()
        self.minio_access_key = form.string_ask(
            "S3 access key (Credentials used to access the VDC's S3)", required=True,
        )
        self.minio_secret_key = form.secret_ask(
            "S3 secret key (Credentials used to access the VDC's S3)", min_length=8, required=True,
        )
        form.ask()

    @chatflow_step(title="VDC Information")
    def vdc_info(self):
        self._init()
        self._vdc_form()
        self._k3s_and_minio_form()

    @chatflow_step(title="VDC Deployment")
    def deploy(self):
        self.vdc = j.sals.vdc.new(
            vdc_name=self.vdc_name.value, owner_tname=self.username, flavor=VDC_SIZE.VDCFlavor[self.vdc_flavor],
        )
        trans_hash = self.vdc.show_vdc_payment(self)
        if not trans_hash:
            j.sals.vdc.delete(self.vdc.vdc_name)
            self.stop(f"payment timedout")
        self.md_show_update("Payment successful")

        try:
            self.deployer = self.vdc.get_deployer(password=self.vdc_secret.value, bot=self)
        except Exception as e:
            j.logger.error(f"failed to initialize vdc deployer due to error {str(e)}")
            self.vdc.refund_payment(trans_hash)
            j.sals.vdc.delete(self.vdc.vdc_name)
            self.stop("failed to initialize vdc deployer. please contact support")

        self.md_show_update("Deploying your VDC...")
        old_wallet = self.deployer._set_wallet(j.core.config.get("VDC_INITIALIZATION_WALLET"))
        try:
            self.config = self.deployer.deploy_vdc(
                minio_ak=self.minio_access_key.value, minio_sk=self.minio_secret_key.value,
            )
            if not self.config:
                self.stop("Failed to deploy vdc. please try again later")
            self.public_ip = self.vdc.kubernetes[0].public_ip
        except j.exceptions.Runtime as err:
            j.logger.error(str(err))
            self.stop(str(err))
        self.deployer._set_wallet(old_wallet)
        self.deployer.renew_plan(14 - INITIAL_RESERVATION_DURATION / 24)

    @chatflow_step(title="Expose S3", disable_previous=True)
    def expose_s3(self):
        result = self.single_choice(
            "Do you wish to expose your S3 over public domain name?", ["Yes", "No"], default="No",
        )
        if result == "YES":
            domain_name = self.deployer.expose_s3()
            self.md_show(f"You can access your S3 cluster over domain {domain_name}")

    @chatflow_step(title="VDC Deployment Success", final_step=True)
    def success(self):
        msg = dedent(
            f"""\
        # Your VDC {self.vdc.vdc_name} has been deployed successfuly.
        <br />\n
        Please download the config file to `~/.kube/config` to start using your cluster with [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)

        Kubernetes controller public IP: {self.public_ip}
        """
        )
        self.download_file(
            msg, self.config, f"{self.vdc.vdc_name}.yaml", md=True,
        )


chat = VDCDeploy
