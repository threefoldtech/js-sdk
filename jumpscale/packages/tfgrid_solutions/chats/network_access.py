from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import StopChatFlow, chatflow_step
from jumpscale.sals.reservation_chatflow import deployer, deployment_context
from jumpscale.packages.tfgrid_solutions.sals.network_chat_base import NetworkBase


class NetworkAccess(NetworkBase):
    steps = ["start", "ip_config", "access_node_selection", "network_reservation", "network_info"]
    title = "Network Access"

    @chatflow_step(title="Network Name")
    def start(self):
        super().start()
        if not self.kwargs.get("name"):
            self.network_view = deployer.select_network(self)
        else:
            self.network_view = deployer.get_network_view(self.kwargs["name"])
            if not self.network_view:
                raise StopChatFlow(f"no network named {self.kwargs['name']}")

    @chatflow_step(title="Reservation")
    @deployment_context()
    def network_reservation(self):
        try:
            self.config = deployer.add_access(
                self.network_view.name,
                self.network_view,
                self.access_node.node_id,
                self.pool,
                self.ipversion == "IPv4",
                bot=self,
                **self.solution_metadata,
            )
        except Exception as e:
            raise StopChatFlow(f"Failed to register workload due to error {str(e)}")

        super().network_reservation()


chat = NetworkAccess
