import { ExternalView } from "../external";

// TODO: Change URL when jupyter is supported
const URL = "https://www.threefold.io";

export default class JupyterView extends ExternalView {
    constructor(app, name) {
        super(app, name, URL);
    }
}
