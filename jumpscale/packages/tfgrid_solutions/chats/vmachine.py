import uuid
from jumpscale.loader import j
from textwrap import dedent
from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step
from jumpscale.sals.reservation_chatflow import DeploymentFailed, deployer, deployment_context, solutions
from jumpscale.clients.explorer.models import VMSIZES


class VMachineDeploy(GedisChatBot):
    steps = [
        "vm_name",
        "choose_flavor",
        "add_public_ip",
        "select_pool",
        "network_selection",
        "ip_selection",
        "public_key_get",
        "reservation",
        "success",
    ]
    title = "VMachine"

    def _deployment_start(self):
        deployer.chatflow_pools_check()
        deployer.chatflow_network_check(self)
        self.solution_id = uuid.uuid4().hex
        self.solution_metadata = {}

    @chatflow_step(title="Solution Name")
    def vm_name(self):
        self._deployment_start()
        valid = False
        while not valid:
            self.solution_name = deployer.ask_name(self)
            vm_solutions = solutions.list_vmachine_solutions(sync=False)
            valid = True
            for sol in vm_solutions:
                if sol["Name"] == self.solution_name:
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
        self.vm_query = VMSIZES.get(self.vm_size)

    @chatflow_step(title="Public IP")
    def add_public_ip(self):
        choices = ["Yes", "No"]
        choice = self.single_choice("Do you want to enable public IP", choices, default="Yes", required=True)
        self.enable_public_ip = False
        self.vm_query.update({"ipv4u": 0})
        if choice == "Yes":
            self.enable_public_ip = True
            self.vm_query.update({"ipv4u": 1})

    @chatflow_step(title="Select Pools")
    def select_pool(self):
        workload_name = self.solution_name
        cloud_units = j.sals.marketplace.deployer._calculate_cloud_units(**self.vm_query)
        self.pool_id = deployer.select_pool(self, cu=cloud_units.cu, su=cloud_units.su, **self.vm_query)
        if not self.pool_id:
            raise DeploymentFailed(
                f"Failed to find a node with the required resources CRU: {self.vm_query.get('cru')}, MRU: {self.vm_query.get('mru', 0)}, CRU: {self.vm_query.get('cru', 0)}, SRU: {self.vm_query.get('sru', 0)}, IPV4U: {self.vm_query.get('ipv4u', 0)}"
            )
        self.selected_nodes = list(
            j.sals.zos.get(self.solution_metadata.get("owner")).nodes_finder.nodes_by_capacity(
                pool_id=self.pool_id, cru=self.vm_query["cru"], mru=self.vm_query["mru"], sru=self.vm_query["sru"]
            )
        )

        if not self.selected_nodes:
            raise DeploymentFailed(
                f"Failed to find a node with the required resources CRU: {self.vm_query.get('cru', 0)}, MRU: {self.vm_query.get('mru', 0)}, CRU: {self.vm_query.get('cru', 0)}, SRU: {self.vm_query.get('sru')}"
            )

    @chatflow_step(title="Network")
    def network_selection(self):
        self.network_view = deployer.select_network(self, self.all_network_viewes)

    @chatflow_step(title="Access keys and secret")
    def public_key_get(self):
        self.ssh_keys = self.upload_file(
            """Please upload your public SSH key to be able to access the deployed VM via ssh
                Note: please use keys compatible with Dropbear server eg: RSA""",
            required=True,
        ).splitlines()

    @chatflow_step(title="IP selection")
    @deployment_context()
    def ip_selection(self):
        self.md_show_update("Deploying Network on Nodes....")
        self.network_view_copy = self.network_view.copy()
        result = deployer.add_network_node(
            self.network_view.name,
            self.selected_nodes[0],
            self.pool_id,
            self.network_view,
            self,
            owner=self.solution_metadata.get("owner"),
        )
        if result:
            self.md_show_update("Deploying Network on Node....")
            for wid in result["ids"]:
                success = deployer.wait_workload(wid, self, breaking_node_id=self.selected_node.node_id)
                if not success:
                    raise DeploymentFailed(f"Failed to add node {self.selected_node.node_id} to network {wid}", wid=wid)
            self.network_view_copy = self.network_view_copy.copy()
        free_ips = self.network_view_copy.get_node_free_ips(self.selected_nodes[0])
        self.ip_address = self.drop_down_choice(
            "Please choose IP Address for your solution", free_ips, default=free_ips[0], required=True,
        )

    @chatflow_step(title="Virtual machine reservations", disable_previous=True)
    @deployment_context()
    def reservation(self):
        metadata = {
            "name": self.solution_name,
            "form_info": {"chatflow": "vmachine", "Solution name": self.solution_name},
        }
        self.reservation, self.public_ip = deployer.deploy_vmachine(
            node_id=self.selected_nodes[0].node_id,
            network_name=self.network_view.name,
            name="ubuntu-20.04",
            ip_address=self.ip_address,
            ssh_keys=self.ssh_keys,
            pool_id=self.pool_id,
            size=self.vm_size,
            enable_public_ip=self.enable_public_ip,
            **self.solution_metadata,
        )

        success = deployer.wait_workload(self.reservation, self)
        if not success:
            raise DeploymentFailed(
                f"Failed to deploy workload {self.reservation}", solution_uuid=self.solution_id, wid=self.reservation,
            )

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        ip = self.public_ip if self.public_ip else self.ip_address
        res = f"""\
        # Your virtual machine has been deployed successfully:
        <br />\n
        - IP: {ip}
        - To connect: `ssh root@{ip}`
            <br />\n
        """
        self.md_show(dedent(res))


chat = VMachineDeploy
