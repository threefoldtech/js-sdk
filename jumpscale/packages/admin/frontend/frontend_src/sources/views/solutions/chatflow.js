import { ExternalView } from "../external";

const REQUIRED_PACKAGES = {
    "tfgrid_solutions": "https://github.com/threefoldtech/js-sdk/blob/development/jumpscale/packages/tfgrid_solutions"
}

export default class ChatflowView extends ExternalView {
    constructor(app, name) {
        super(app, name, "", REQUIRED_PACKAGES);
    }

    urlChange(view, url) {
        const params = url[0].params;
        if (Object.keys(params).length !== 2) {
            return;
        }

        this.targetUrl = `/${params.package}/chats/${params.chat}#/?noheader=yes`;
        this.init(view);
    }
}
