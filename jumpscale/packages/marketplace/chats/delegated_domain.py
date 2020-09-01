import uuid

from jumpscale.packages.tfgrid_solutions.chats.delegated_domain import DomainDelegation as BaseDomainDelegation
from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.sals.marketplace import MarketPlaceChatflow, deployer


class DomainDelegation(BaseDomainDelegation, MarketPlaceChatflow):
    @chatflow_step(title="Pool")
    def select_pool(self):
        self._validate_user()
        self.solution_id = uuid.uuid4().hex
        self.username = self.user_info()["username"]
        self.solution_metadata = {"owner": self.username}
        self.gateway, pool = deployer.select_gateway(self.solution_metadata["owner"], bot=self)
        self.pool_id = pool.pool_id


chat = DomainDelegation
