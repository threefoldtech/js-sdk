import { Service } from "../common/api";

const BASE_URL = "/tfgrid_solutions/actors/solutions";

class SolutionsService extends Service {
    constructor() {
        super(BASE_URL);
    }

    listAllSolutions(){
        return this.getCall("list_all_solutions")
    }

    listSolution(solutionType){
        return this.postCall("list_solutions",{solution_type: solutionType})
    }

    delete(solutionType, solutionName) {
        return this.postCall("cancel_solution", { solution_type: solutionType, solution_name: solutionName });
    }

    count(){
        return this.getCall("count_solutions")
    }
}

export const solutions = new SolutionsService();
