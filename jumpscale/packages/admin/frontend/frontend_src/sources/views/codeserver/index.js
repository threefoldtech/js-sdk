import { ExternalView } from "../external";

// TODO: Change URL when codeserver is supported
const URL = "https://www.threefold.io";

export default class CodeserverView extends ExternalView {
    constructor(app, name) {
        super(app, name, URL);
    }
}
