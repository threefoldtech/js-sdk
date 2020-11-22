from jumpscale.loader import j
from jumpscale.servers.gedis.baseactor import BaseActor, actor_method

# from shlex import quote
# from kubernetes import client, config


class Solutions(BaseActor):
    def __init__(self):
        super().__init__()
        k8s_client = j.sals.kubernetes.Manager()

    @actor_method
    def list_all_solutions(self, solution_type: str) -> str:

        return j.data.serializers.json.dumps("")


Actor = Solutions
