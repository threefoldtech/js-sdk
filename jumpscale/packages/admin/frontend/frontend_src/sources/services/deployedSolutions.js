import { Service } from "../common/api";

const BASE_URL = "/admin/actors/solutions";

class SolutionsService extends Service {
    constructor() {
        super(BASE_URL);
    }

    list(opts) {
        opts = opts || {};
        return this.getCall("solutions_list");
    }

    listSolution(solutionType){
        return this.postCall("solutions_list",{solution_type: solutionType})
    }

    delete(solutionType, solutionName) {
        return this.postCall("solution_delete", { solution_type: solutionType, solution_name: solutionName });
    }
}

export const solutions = new SolutionsService();
