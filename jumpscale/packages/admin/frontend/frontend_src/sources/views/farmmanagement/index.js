import { ExternalView } from "../external";

const URL = "/farmmanagement/frontend/";
// TODO: Add required package

export default class FarmmanagementView extends ExternalView {
    constructor(app, name) {
        super(app, name, URL);
    }
}
