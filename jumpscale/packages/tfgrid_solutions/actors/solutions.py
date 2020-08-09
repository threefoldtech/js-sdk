import json
from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.loader import j
from jumpscale.core.exceptions import JSException
from jumpscale.sals.reservation_chatflow.models import SolutionType
from jumpscale.sals.reservation_chatflow import solutions, deployer
from jumpscale.clients.explorer.conversion import AlreadyConvertedError


class Solutions(BaseActor):
    @actor_method
    def list_all_solutions(self) -> str:
        res = []
        for workload in j.sals.zos.workloads.list(j.core.identity.me.tid):
            w_dict = workload.to_dict()
            w_dict["workload_type"] = workload.info.workload_type.name
            w_dict["pool_id"] = workload.info.pool_id
            res.append(w_dict)
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
        farm_names = {}
        for pool in j.sals.zos.pools.list():
            pool_dict = pool.to_dict()
            farm_id = deployer.get_pool_farm_id(pool.pool_id)
            farm = farm_names.get(farm_id)
            if not farm:
                farm = deployer._explorer.farms.get(farm_id)
                farm_names[farm_id] = farm
            pool_dict["farm"] = farm.name
            res.append(pool_dict)
        return j.data.serializers.json.dumps({"data": res})


Actor = Solutions
