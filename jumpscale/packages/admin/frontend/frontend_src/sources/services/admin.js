import { Service } from "../common/api";

const BASE_URL = "/admin/actors/myactor";

class AdminService extends Service {
    constructor() {
        super(BASE_URL);
    }

    hello() {
        return this.getCall("hello");
    }
}

export const admin = new AdminService();
