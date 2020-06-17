import { Service } from "../common/api";

const BASE_URL = "/tfgrid_solutions/actors/solutions";

class SolutionsService extends Service {
    constructor() {
        super(BASE_URL);
    }

    listSolution(solutionType){
        return this.postCall("list_solutions",{solution_type: solutionType})
    }

    delete(solutionType, solutionName) {
        return this.postCall("solution_delete", { solution_type: solutionType, solution_name: solutionName });
    }
}

export const solutions = new SolutionsService();
