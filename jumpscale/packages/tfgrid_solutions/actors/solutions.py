from jumpscale.clients.explorer.conversion import AlreadyConvertedError
from jumpscale.core.base import StoredFactory
from jumpscale.loader import j
from jumpscale.packages.tfgrid_solutions.models import PoolConfig
from jumpscale.sals.reservation_chatflow import solutions
from jumpscale.servers.gedis.baseactor import BaseActor, actor_method


class Solutions(BaseActor):
    @actor_method
    def list_all_solutions(self) -> str:
        res = []
        for workload in j.sals.zos.workloads.list(j.core.identity.me.tid):
            w_dict = workload.to_dict()
            w_dict["workload_type"] = workload.info.workload_type.name
            w_dict["pool_id"] = workload.info.pool_id
            w_dict["epoch"] = workload.info.epoch.timestamp()
            w_dict["next_action"] = workload.info.next_action.name
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
    def list_pools(self, include_hidden) -> str:
        res = j.sals.reservation_chatflow.solutions.list_pool_solutions(include_hidden)
        return j.data.serializers.json.dumps({"data": res})

    @actor_method
    def cancel_workload(self, wid) -> bool:
        j.sals.zos.workloads.decomission(wid)
        return True

    @actor_method
    def patch_cancel_workloads(self, wids) -> bool:
        for wid in wids:
            j.sals.zos.workloads.decomission(wid)
        return True

    @actor_method
    def rename_pool(self, pool_id, name) -> str:
        pool_factory = StoredFactory(PoolConfig)
        if f"pool_{pool_id}" in pool_factory.list_all():
            local_config = pool_factory.get(f"pool_{pool_id}")
        else:
            local_config = pool_factory.new(f"pool_{pool_id}")
            local_config.pool_id = pool_id
        local_config.name = name
        local_config.save()
        return j.data.serializers.json.dumps(local_config.to_dict())

    @actor_method
    def hide_pool(self, pool_id) -> bool:
        pool_factory = StoredFactory(PoolConfig)
        if f"pool_{pool_id}" in pool_factory.list_all():
            local_config = pool_factory.get(f"pool_{pool_id}")
        else:
            local_config = pool_factory.new(f"pool_{pool_id}")
            local_config.pool_id = pool_id
        local_config.hidden = True
        local_config.save()
        return True

    @actor_method
    def unhide_pool(self, pool_id) -> bool:
        pool_factory = StoredFactory(PoolConfig)
        if f"pool_{pool_id}" in pool_factory.list_all():
            local_config = pool_factory.get(f"pool_{pool_id}")
            local_config.hidden = False
            local_config.save()
        return True


Actor = Solutions
