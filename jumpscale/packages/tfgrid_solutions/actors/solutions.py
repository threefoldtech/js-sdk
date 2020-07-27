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
        listings = {
            "network": solutions.list_network_solutions,
            "ubuntu": solutions.list_ubuntu_solutions,
            "flist": solutions.list_flist_solutions,
            "minio": solutions.list_minio_solutions,
            "kubernetes": solutions.list_kubernetes_solutions,
            "gitea": solutions.list_gitea_solutions,
            "4to6gw": solutions.list_4to6gw_solutions,
            "delegated_domain": solutions.list_delegated_domain_solutions,
            "exposed": solutions.list_exposed_solutions,
            "monitoring": solutions.list_monitoring_solutions,
        }

        result = []
        if solution_type in listings:
            result = listings[solution_type]()

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


Actor = Solutions
