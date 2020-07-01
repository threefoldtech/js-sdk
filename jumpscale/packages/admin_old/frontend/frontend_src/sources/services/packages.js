import { Service } from "../common/api";

const BASE_URL = "/admin/actors/packages";

class PackagesService extends Service {
    constructor() {
        super(BASE_URL);
    }

    getStatus(names) {
        return this.postCall("get_package_status", {
            names: names
        });
    }

    list() {
        return this.getCall("list_packages");
    }

    add(path, gitUrl) {
        return this.postCall("add_package", {
            path: path || "",
            giturl: gitUrl || ""
        });
    }

    delete(packageName) {
        return this.postCall("delete_package", { name: packageName });
    }
}

export const packages = new PackagesService();
