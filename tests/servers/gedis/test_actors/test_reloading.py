from jumpscale.servers.gedis.baseactor import BaseActor, actor_method


class TestReloadingActor(BaseActor):
    @actor_method
    def get_value(self) -> int:
        """returns a known value"""
        return 1


Actor = TestReloadingActor
