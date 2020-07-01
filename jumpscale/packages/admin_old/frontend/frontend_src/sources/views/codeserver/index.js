import { ExternalView } from "../external";

// TODO: modify url to be development branch
const URL = "/codeserver/";
const REQUIRED_PACKAGES = {
    "codeserver": "https://github.com/threefoldtech/js-sdk/blob/development/jumpscale/packages/codeserver"
}

export default class CodeserverView extends ExternalView {
    constructor(app, name) {
        super(app, name, URL, REQUIRED_PACKAGES);
    }
}
