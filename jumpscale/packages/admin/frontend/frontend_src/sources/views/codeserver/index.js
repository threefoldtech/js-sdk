import { ExternalView } from "../external";

const URL = "https://www.threefold.io";

export default class CodeserverView extends ExternalView {
    constructor(app, name) {
        super(app, name, URL);
    }
}
