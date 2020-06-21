import { ExternalView } from "../external";
import { admin } from "../../services/admin";

export default class CapacityView extends ExternalView {
    constructor(app, name) {
        super(app, name);
    }

    showIframe() {
        admin.getExplorer().then((data) => {
            const explorer = JSON.parse(data.json()).data;
            let url = explorer.url;

            if (!url.startsWith('http')) {
                url = `https://${url}`;
            }

            this.externalIframe.show();
            this.externalIframe.showProgress({ type: "icon" });
            this.externalIframe.load(url);
        })
    }
}
