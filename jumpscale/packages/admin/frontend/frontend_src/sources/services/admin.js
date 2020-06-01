import { Service } from "../common/api";

const BASE_URL = "/admin/actors/admin";

class AdminService extends Service {
    constructor() {
        super(BASE_URL);
    }

    list() {
        return this.getCall("admin_list");
    }


    add(name) {
        return this.postCall("admin_add", {
            "name": name
        });
    }

    delete(name) {
        return this.postCall("admin_delete", {
            "name": name
        });
    }

    getExplorer() {
        return this.getCall('get_explorer');
    }

    setExplorer(type) {
        // post call to send args as json
        return this.postCall('set_explorer', {
            explorer_type: type
        })
    }
}

export const admin = new AdminService();
