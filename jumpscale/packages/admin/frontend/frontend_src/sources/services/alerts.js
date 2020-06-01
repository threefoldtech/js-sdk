import { Service } from "../common/api";

const BASE_URL = "/admin/actors/alerts";

class AlertsService extends Service {
    constructor() {
        super(BASE_URL);
    }

    list() {
        return this.getCall("list_alerts");
    }

    delete(identifiers) {
        return this.postCall("delete_alerts", {
            identifiers: identifiers
        });
    }
}

export const alerts = new AlertsService();
