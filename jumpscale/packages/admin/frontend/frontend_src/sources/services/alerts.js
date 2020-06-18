import { Service } from "../common/api";

const BASE_URL = "/admin/actors/alerts";

class AlertsService extends Service {
    constructor() {
        super(BASE_URL);
    }

    list() {
        return this.getCall("list_alerts");
    }

    count() {
        return this.getCall("get_alerts_count");
    }

    delete(ids, identifiers) {
        return this.postCall("delete_alerts", {
            ids: ids,
            identifiers: identifiers
        });
    }
}

export const alerts = new AlertsService();
