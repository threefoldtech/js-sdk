from io import SEEK_CUR
from jumpscale.sals.vdc import deployer
from jumpscale.loader import j
from jumpscale.sals.vdc.size import VDC_SIZE, INITIAL_RESERVATION_DURATION
from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step, StopChatFlow
from textwrap import dedent


class VDCDeploy(GedisChatBot):
    title = "VDC"
    steps = ["vdc_info", "deploy", "success"]

    def _init(self):
        self.md_show_update("Checking payment service...")
        # check stellar service
        if not j.clients.stellar.check_stellar_service():
            raise StopChatFlow("Payment service is currently down, try again later")
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
            is_identifier=True,
        )
        self.vdc_secret = form.secret_ask("VDC Secret (Secret for controlling the vdc)", min_length=8, required=True,)
        self.vdc_flavor = form.single_choice(
            "Choose the VDC plan", options=vdc_flavor_messages, default=vdc_flavor_messages[0], required=True,
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
        # self._k3s_and_minio_form() # TODO: Restore later

    @chatflow_step(title="VDC Deployment")
    def deploy(self):
        self.vdc = j.sals.vdc.new(
            vdc_name=self.vdc_name.value, owner_tname=self.username, flavor=VDC_SIZE.VDCFlavor[self.vdc_flavor],
        )
        try:
            self.vdc.prepaid_wallet
            self.vdc.provision_wallet
        except Exception as e:
            j.sals.vdc.delete(self.vdc.instance_name)
            j.logger.error(f"failed to initialize wallets for VDC {self.vdc_name.value} due to error {str(e)}")
            self.stop(f"failed to initialize VDC wallets. please try again later")

        success, amount, payment_id = self.vdc.show_vdc_payment(self)
        if not success:
            j.sals.vdc.delete(self.vdc.instance_name)  # delete it?
            self.stop(f"payment timedout")
        self.md_show_update("Payment successful")

        try:
            self.deployer = self.vdc.get_deployer(password=self.vdc_secret.value, bot=self)
        except Exception as e:
            j.logger.error(f"failed to initialize VDC deployer due to error {str(e)}")
            j.sals.billing.issue_refund(payment_id)
            j.sals.vdc.delete(self.vdc.instance_name)
            self.stop("failed to initialize VDC deployer. please contact support")

        self.md_show_update("Deploying your VDC...")
        initialization_wallet_name = j.core.config.get("VDC_INITIALIZATION_WALLET")
        old_wallet = self.deployer._set_wallet(initialization_wallet_name)
        try:
            self.config = self.deployer.deploy_vdc(minio_ak="12345678", minio_sk="12345678",)
            if not self.config:
                raise StopChatFlow("Failed to deploy VDC due to invlaid kube config. please try again later")
            self.public_ip = self.vdc.kubernetes[0].public_ip
        except Exception as err:
            j.logger.error(str(err))
            self.deployer.rollback_vdc_deployment()
            j.sals.billing.issue_refund(payment_id)
            j.sals.vdc.delete(self.vdc.vdc_name)
            self.stop(str(err))
        self.md_show_update("Adding funds to provisioning wallet...")
        initial_transaction_hashes = self.deployer.transaction_hashes
        try:
            self.vdc.transfer_to_provisioning_wallet(amount / 2)
        except Exception as e:
            j.sals.billing.issue_refund(payment_id)
            j.sals.vdc.delete(self.vdc.instance_name)
            j.logger.error(f"failed to fund provisioning wallet due to error {str(e)} for vdc: {self.vdc.vdc_name}.")
            raise StopChatFlow(f"failed to fund provisioning wallet due to error {str(e)}")

        if initialization_wallet_name:
            try:
                self.vdc.pay_initialization_fee(initial_transaction_hashes, initialization_wallet_name)
            except Exception as e:
                j.logger.critical(f"failed to pay initialization fee for vdc: {self.vdc.solution_uuid}")
        self.deployer._set_wallet(old_wallet)
        self.md_show_update("Updating expiration...")
        self.deployer.renew_plan(14 - INITIAL_RESERVATION_DURATION / 24)

    @chatflow_step(title="VDC Deployment Success", final_step=True)
    def success(self):
        msg = dedent(
            f"""\
        # Your VDC {self.vdc.vdc_name} has been deployed successfuly.
        <br />\n
        Please download the config file to `~/.kube/config` to start using your cluster with [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)

        Kubernetes controller public IP: {self.public_ip}
        <br />\n
        `WARINING: Please keep the kubeconfig file safe and secure. Anyone who has this file can access the kubernetes cluster`
        """
        )

        self.download_file(
            msg, self.config, f"{self.vdc.vdc_name}.yaml", md=True,
        )


chat = VDCDeploy
