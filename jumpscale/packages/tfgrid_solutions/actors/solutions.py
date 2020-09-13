import json
from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.loader import j
from jumpscale.packages.tfgrid_solutions.models import PoolConfig
from jumpscale.core.base import StoredFactory
from jumpscale.sals.reservation_chatflow import solutions, deployer
from jumpscale.clients.explorer.conversion import AlreadyConvertedError
from jumpscale.clients.explorer.models import NextAction


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
        res = []
        farm_names = {}
        pool_factory = StoredFactory(PoolConfig)
        workloads_dict = {w.id: w for w in j.sals.zos.workloads.list(j.core.identity.me.tid, NextAction.DEPLOY)}
        for pool in j.sals.zos.pools.list():
            if not pool.node_ids:
                continue
            hidden = False
            name = ""
            if f"pool_{pool.pool_id}" in pool_factory.list_all():
                local_config = pool_factory.get(f"pool_{pool.pool_id}")
                hidden = local_config.hidden
                name = local_config.name

            if not include_hidden and hidden:
                continue

            pool_dict = pool.to_dict()
            pool_dict["name"] = name
            pool_dict["hidden"] = hidden
            pool_dict["explorer_url"] = j.core.identity.me.explorer_url
            farm_id = deployer.get_pool_farm_id(pool.pool_id)
            if farm_id >= 0:
                farm = farm_names.get(farm_id)
                if not farm:
                    farm = deployer._explorer.farms.get(farm_id)
                    farm_names[farm_id] = farm
                pool_dict["farm"] = farm.name
            for i, wid in enumerate(pool_dict["active_workload_ids"]):
                if wid in workloads_dict:
                    pool_dict["active_workload_ids"][i] = f"{workloads_dict[wid].info.workload_type.name} - {wid}"
                else:
                    # due to differnet next action. we'll just show the id
                    pool_dict["active_workload_ids"][i] = wid
            res.append(pool_dict)
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
