from jumpscale.packages.tfgrid_solutions.chats.cryptpad_deploy import CryptpadDeploy as BaseCryptpadDeploy
from jumpscale.sals.chatflows.chatflows import chatflow_step, StopChatFlow
from jumpscale.sals.marketplace import MarketPlaceChatflow, deployer, solutions
import uuid
import random

FARM_NAMES = ["freefarm"]


class UbuntuDeploy(MarketPlaceChatflow):
    steps = [
        "ubuntu_start",
        "ubuntu_name",
        "ubuntu_info",
        "ubuntu_expiration",
        "public_key_get",
        "pool_preparation",
        "reservation",
        "ubuntu_access",
    ]

    @chatflow_step()
    def ubuntu_start(self):
        self._validate_user()
        self.md_show("This wizard will help you deploy ubuntu container")
        self.solution_metadata = dict()
        self.solution_id = uuid.uuid4().hex
        self.solution_metadata["owner"] = self.user_info()["username"]

    @chatflow_step()
    def ubuntu_name(self):
        self.md_show_update("Fetching Infromation...")
        used_names = [s["Name"] for s in solutions.list_ubuntu_solutions(self.solution_metadata["owner"])]
        valid = False
        while not valid:
            self.solution_name = self.string_ask("Please enter a name for your ubuntu container", required=True)
            if self.solution_name in used_names:
                self.md_show("name already used. please click next to continue")
            else:
                valid = True
        self.solution_name = f"{self.solution_metadata['owner']}_{self.solution_name}"

    @chatflow_step()
    def ubuntu_info(self):
        form = self.new_form()
        self.currency = form.single_choice("please select the currency you wish ", ["TFT", "TFTA"], required=True)
        form.ask()
        self.currency = self.currency.value
        self.query = {"cru": 1, "mru": 1, "sru": 1}

    @chatflow_step()
    def ubuntu_expiration(self):
        self.expiration = deployer.ask_expiration(self)

    @chatflow_step(title="Access keys")
    def public_key_get(self):
        self.public_key = self.upload_file(
            """Please add your public ssh key, this will allow you to access the deployed container using ssh.
                    Just upload the file with the key""",
            required=True,
        ).split("\n")[0]

    @chatflow_step()
    def pool_preparation(self):
        # this step provisions the pool for the solution and network if he is new user.
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
            raise StopChatFlow("Bye bye")

        # get ip address
        self.network_view = deployer.get_network_view(f"{self.solution_metadata['owner']}_apps")
        self.ip_address = None
        while not self.ip_address:
            self.selected_node = deployer.schedule_container(self.pool_info.reservation_id, **self.query)
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

    @chatflow_step(title="Reservation")
    def reservation(self):
        container_flist = f"https://hub.grid.tf/tf-bootable/3bot-ubuntu-18.04.flist"
        metadata = {
            "name": self.solution_name,
            "form_info": {"chatflow": "ubuntu", "Solution name": self.solution_name},
        }
        self.solution_metadata.update(metadata)
        self.resv_id = deployer.deploy_container(
            pool_id=self.pool_info.reservation_id,
            node_id=self.selected_node.node_id,
            network_name=self.network_view.name,
            ip_address=self.ip_address,
            flist=container_flist,
            cpu=1,
            memory=1024,
            env={"pub_key": self.public_key},
            interactive=False,
            entrypoint="/bin/bash /start.sh",
            **self.solution_metadata,
            solution_uuid=self.solution_id,
        )
        success = deployer.wait_workload(self.resv_id, self)
        if not success:
            raise StopChatFlow(f"Failed to deploy workload {self.resv_id}")

    @chatflow_step(title="Success", disable_previous=True)
    def ubuntu_access(self):
        self.download_file(msg=f"<pre>{self.wgconf}</pre>", data=self.wgconf, filename="apps.conf", html=True)
        res = f"""\
    # Ubuntu has been deployed successfully: your reservation id is: {self.resv_id}
    \n<br />\n
    To connect ```ssh root@{self.ip_address}``` .It may take a few minutes.
                    """
        self.md_show(res, md=True)


chat = UbuntuDeploy
