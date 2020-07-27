import json
from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.loader import j
from jumpscale.core.exceptions import JSException
from jumpscale.sals.reservation_chatflow.models import SolutionType
from jumpscale.sals.reservation_chatflow import solutions
from jumpscale.clients.explorer.conversion import AlreadyConvertedError


class Solutions(BaseActor):
    @actor_method
    def list_all_solutions(self) -> str:
        res = [workload.to_dict() for workload in j.sals.zos.workloads.list(j.core.identity.me.tid)]
        return j.data.serializers.json.dumps({"data": res})

    @actor_method
    def list_solutions(self, solution_type: str) -> str:
        result = []
        method_name = f"list_{solution_type}_solutions"
        if hasattr(solutions, method_name):
            result = getattr(solutions, method_name)()

        return j.data.serializers.json.dumps({"data": result})

    @actor_method
    def cancel_solution(self, wids) -> bool:
        solutions.cancel_solution(wids)
        return True

    @actor_method
    def count_solutions(self) -> str:
        res = solutions.count_solutions()
        return j.data.serializers.json.dumps({"data": res})

    @actor_method
    def has_migrated(self) -> str:
        try:
            if j.sals.zos._explorer.conversion.initialize():
                return j.data.serializers.json.dumps({"result": False})
        except AlreadyConvertedError:
            pass
        return j.data.serializers.json.dumps({"result": True})

    @actor_method
    def migrate(self) -> str:
        j.sals.zos.conversion()
        return j.data.serializers.json.dumps({"result": True})

    @actor_method
    def list_pools(self) -> str:
        res = []
        for pool in j.sals.zos.pools.list():
            res.append(pool.to_dict())
        return j.data.serializers.json.dumps(res)


Actor = Solutions
