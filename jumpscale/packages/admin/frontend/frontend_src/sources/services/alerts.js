import { Service } from "../common/api";

const BASE_URL = "/admin/actors/alerts";

class AlertsService extends Service {
    constructor() {
        super(BASE_URL);
    }

    list() {
        return this.getCall("alerts_list");
    }

    count() {
        return this.getCall("alerts_count");
    }

    delete(ids, identifiers) {
        return this.postCall("alerts_delete", {
            ids: ids,
            identifiers: identifiers
        });
    }
}

export const alerts = new AlertsService();
