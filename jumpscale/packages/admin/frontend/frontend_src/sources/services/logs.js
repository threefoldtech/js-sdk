import { Service } from "../common/api";

const BASE_URL = "/admin/actors/logs";

class LogsService extends Service {
    constructor() {
        super(BASE_URL);
    }

    listApps() {
        return this.getCall("list_apps");
    }

    listLogs(appName, limit) {
        return this.postCall("list_logs", {appname: appName, limit: limit});
    }

    delete(appname){
        return this.postCall("remove_records",{
            appname: appname
        })
    }

    deleteAll(){
        return this.postCall("remove_records")
    }

}

export const logs = new LogsService();
