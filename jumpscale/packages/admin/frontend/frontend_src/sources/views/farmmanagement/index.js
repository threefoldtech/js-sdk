import { ExternalView } from "../external";

// TODO: modify url to be development branch
const URL = "/farmmanagement/";
const REQUIRED_PACKAGES = {
    "farmmanagement": "https://github.com/threefoldtech/js-sdk/blob/development/jumpscale/packages/farmmanagement"
}

export default class FarmmanagementView extends ExternalView {
    constructor(app, name) {
        super(app, name, URL, REQUIRED_PACKAGES);
    }
}
