import { ExternalView } from "../external";

const URL = "https://wiki.threefold.io"

export default class ThreefoldWiki extends ExternalView {
    constructor(app, name) {
        super(app, name, URL);
    }
}
