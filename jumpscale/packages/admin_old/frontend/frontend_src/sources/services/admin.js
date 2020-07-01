import { Service } from "../common/api";

const BASE_URL = "/admin/actors/admin";

class AdminService extends Service {
    constructor() {
        super(BASE_URL);
    }

    list() {
        return this.getCall("list_admins");
    }

    add(name) {
        return this.postCall("add_admin", {
            "name": name
        });
    }

    delete(name) {
        return this.postCall("delete_admin", {
            "name": name
        });
    }

    getCurrentUser() {
        return this.getCall("get_current_user");
    }

    getExplorer() {
        return this.getCall("get_explorer");
    }

    setExplorer(type) {
        // post call to send args as json
        return this.postCall("set_explorer", {
            explorer_type: type
        })
    }
}

export const admin = new AdminService();
