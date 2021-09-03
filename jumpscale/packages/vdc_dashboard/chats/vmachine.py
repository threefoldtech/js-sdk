from textwrap import dedent

from jumpscale.clients.explorer.models import VMSIZES
from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.sals.marketplace import MarketPlaceAppsChatflow
from jumpscale.sals.reservation_chatflow import deployer, solutions
from jumpscale.sals.vdc.deployer import VDCIdentityError
from jumpscale.sals.vdc.scheduler import GlobalCapacityChecker


class VMachineDeploy(MarketPlaceAppsChatflow):
    steps = [
        "vm_name",
        "choose_flavor",
        "public_key_get",
        "add_public_ip",
        "different_farm",
        "select_farm",
        "add_vmachine",
        "success",
    ]
    title = "Virtual Machine"

    def _prepare(self):
        self.md_show_update("Checking payment service...")
        # check stellar service
        if not j.clients.stellar.check_stellar_service():
            self.stop("Payment service is currently down, try again later")
        if not j.sals.vdc.list_all():
            self.stop("Couldn't find any vdcs on this machine, Please make sure to have it configured properly")
        self.vdc_name = list(j.sals.vdc.list_all())[0]
        self.vdc = j.sals.vdc.get(name=self.vdc_name)
        if not self.vdc:
            self.stop(f"VDC {self.vdc_name} doesn't exist")
        self.solution_uuid = j.data.idgenerator.uuid.uuid4().hex
        self.identity_name = j.core.identity.me.instance_name

    @chatflow_step(title="Solution Name")
    def vm_name(self):
        self._prepare()
        valid = False
        self.vdc.load_info()
        while not valid:
            self.solution_name = deployer.ask_name(self)
            vm_solutions = self.vdc.vmachines
            valid = True
            for sol in vm_solutions:
                if sol.name == self.solution_name:
                    valid = False
                    self.md_show("The specified solution name already exists. please choose another name.")
                    break
                valid = True

    @chatflow_step(title="VMachine Flavor")
    def choose_flavor(self):
        form = self.new_form()
        sizes = [
            f"vCPU: {data.get('cru')}, RAM: {data.get('mru')} GiB, Disk Space: {data.get('sru')} GiB"
            for data in VMSIZES.values()
        ]
        vm_size = form.drop_down_choice("Choose the size of your VM", sizes, default=sizes[0])
        form.ask()
        self.vm_size = sizes.index(vm_size.value) + 1
        self.query = VMSIZES.get(self.vm_size)

    @chatflow_step(title="Access keys and secret")
    def public_key_get(self):
        self.ssh_keys = self.upload_file(
            """Please upload your public SSH key to be able to access the deployed VM via ssh
                Note: please use keys compatible with Dropbear server eg: RSA""",
            required=True,
        ).splitlines()

    @chatflow_step(title="Public IP")
    def add_public_ip(self):
        choices = ["Yes", "No"]
        choice = self.single_choice("Do you want to enable public IP", choices, default="Yes", required=True)
        self.enable_public_ip = False
        if choice == "Yes":
            self.enable_public_ip = True

    @chatflow_step(title="Farm Selection")
    def different_farm(self):
        self.diff_farm = False
        diff_farm = self.single_choice(
            "Do you want to deploy this node on a different farm?", options=["Yes", "No"], default="No", required=True
        )
        if diff_farm == "Yes":
            self.diff_farm = True

    @chatflow_step(title="Farm selection")
    def select_farm(self):
        self.farm_name = None
        if self.diff_farm:
            self.vdc.load_info()
            self.md_show_update("Checking the available farms")
            old_node_ids = []
            for k8s_node in self.vdc.kubernetes:
                old_node_ids.append(k8s_node.node_id)
            for vmachine in self.vdc.vmachines:
                old_node_ids.append(vmachine.node_id)
            gcc = GlobalCapacityChecker()
            gcc.exclude_nodes(*old_node_ids)
            farms_names = list(gcc.get_available_farms(**self.query))
            if not farms_names:
                self.stop(f"There's no enough capacity for vmachine node of this size")
            self.farm_name = self.drop_down_choice("Choose a farm to deploy on", options=farms_names, required=True)

    @chatflow_step(title="Deploying virtual machine")
    def add_vmachine(self):
        farm_name, capacity_check = self.vdc.find_vmachine_farm(self.query, self.farm_name, self.enable_public_ip)
        if not capacity_check:
            self.stop(
                f"There's no enough capacity in farm {farm_name} for virtual machine of flavor {self.node_flavor}"
            )
        j.logger.debug("found enough capacity, continue to payment")

        success, _, payment_id = self.vdc.show_external_vmachine_payment(
            self, farm_name=farm_name, size_number=self.vm_size, public_ip=self.enable_public_ip
        )
        if not success:
            self.stop(f"payment timedout (in case you already paid, please contact support)")
        try:
            self.vdc.load_info()
            vdc_deployer = self.vdc.get_deployer(bot=self, network_farm=farm_name)
        except VDCIdentityError:
            self.stop(
                f"Couldn't verify VDC secret. please make sure you are using the correct secret for VDC {self.vdc_name}"
            )
        j.logger.debug(f"Payment success with payment id: {payment_id}")
        self.md_show_update("Payment successful")
        duration = self.vdc.get_pools_expiration() - j.data.time.utcnow().timestamp
        two_weeks = 2 * 7 * 24 * 60 * 60
        if duration > two_weeks:
            duration = two_weeks
        old_wallet = vdc_deployer._set_wallet(self.vdc.prepaid_wallet.instance_name)
        try:
            # Deploy VMachine
            self.result = vdc_deployer.deploy_vmachine(
                farm_name,
                self.solution_name,
                self.query,
                self.vm_size,
                self.ssh_keys,
                enable_public_ip=self.enable_public_ip,
                solution_uuid=self.solution_uuid,
                vmachine_type="ubuntu-20.04",
                duration=duration,
            )
            self.md_show_update("Deployment success...")
        except Exception as e:
            self.stop(f"failed to deploy virtual machine. due to error {str(e)}")

        self.md_show_update("Processing transaction...")
        vdc_deployer._set_wallet(old_wallet)

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        res = f"""\
        # Your virtual machine has been deployed successfully:
        <br />\n
        - Wireguard IP: {self.result.get("ip_address")}
            - To connect: `ssh root@{self.result.get("ip_address")}`
        - Wid: {self.result.get("vm_wid")}
        """
        if self.result.get("public_ip"):
            res += f"""- Public IP: {self.result.get("public_ip")}
            - To connect: `ssh root@{self.result.get("public_ip")}`
            <br />\n
            """
        self.md_show(dedent(res))


chat = VMachineDeploy
