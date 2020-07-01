import { ExternalView } from "../external";

const URL = "https://sdk.threefold.io";

export default class TFGridSDKWiki extends ExternalView {
    constructor(app, name) {
        super(app, name, URL);
    }
}
