import { Service } from "../common/api";

const BASE_URL = "/admin/actors/health";

class HealthService extends Service {
    constructor() {
        super(BASE_URL);
    }

    getDiskSpace() {
        return this.getCall("get_disk_space");
    }

    getHealth() {
        return this.getCall("health");
    }

    getIdentity() {
        return this.getCall("get_identity");
    }

    getNetworkInfo() {
        return this.getCall("network_info");
    }

    getJsxVersion() {
        return this.getCall("jsx_version");
    }

    getRunningProcesses() {
        return this.getCall("get_running_processes");
    }
    getMemoryUsage() {
        return this.getCall("get_memory_usage");
    }
}

export const health = new HealthService();
