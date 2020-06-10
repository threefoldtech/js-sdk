import { ExternalView } from "../external";

const URL = "/codeserver/";

export default class CodeserverView extends ExternalView {
    constructor(app, name) {
        super(app, name, URL);
    }
}
