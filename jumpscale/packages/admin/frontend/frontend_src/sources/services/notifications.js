import { Service } from "../common/api";

const BASE_URL = "/admin/actors/notifications";

class Notifications extends Service {
    constructor() {
        super(BASE_URL);
    }
    
    checkNewRelease() {
        return this.getCall("check_new_release");
    }
}

export const notifications = new Notifications();
