import { Service } from "../common/api";

const BASE_URL = "/admin/actors/packages";

class PackagesService extends Service {
    constructor() {
        super(BASE_URL);
    }

    getStatus(names) {
        return this.postCall("packages_get_status", {
            names: names
        });
    }

    list() {
        return this.getCall("packages_list");
    }

    packagesNames() {
        return this.getCall("packages_names");
    }

    add(path, gitUrl) {
        return this.postCall("package_add", {
            path: path || "",
            giturl: gitUrl || ""
        });
    }

    delete(packageName) {
        return this.postCall("package_delete", { name: packageName });
    }
}

export const packages = new PackagesService();
