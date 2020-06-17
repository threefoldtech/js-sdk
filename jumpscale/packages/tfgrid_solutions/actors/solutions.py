import json
from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.god import j
from jumpscale.core.exceptions import JSException
from jumpscale.sals.reservation_chatflow.models import SolutionType


class TFgridSolutions(BaseActor):
    @actor_method
    def list_solutions(self, solution_type:str) -> str:
        # Update the solutions from the explorer
        j.sals.reservation_chatflow.get_solutions_explorer()
        
        solutions = []
        solutions = j.sals.reservation_chatflow.get_solutions(SolutionType[solution_type])
        return j.data.serializers.json.dumps({"data":solutions})

    # @actor_method
    # def cancel_reservation(self, solution_type, solution_name):
    #     if solution_type:
    #         j.sal.reservation_chatflow.reservation_cancel_for_solution(solution_name)
    #         return True
    #     return False

Actor = TFgridSolutions