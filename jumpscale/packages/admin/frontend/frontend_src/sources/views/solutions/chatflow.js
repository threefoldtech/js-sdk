import { ExternalView } from "../external";

export default class ChatflowView extends ExternalView {
    constructor(app, name) {
        super(app, name);
        // TODO: modify url to be development branch
        this.baseGitUrl = "https://github.com/threefoldtech/js-sdk/blob/development_adminpanel/jumpscale/packages/tfgrid_solutions";

    }

    urlChange(view, url) {
        const params = url[0].params;
        if (Object.keys(params).length !== 2) {
            return;
        }

        const packageName = `${params.package}`
        const packageUrl = packageName.replace(".", "/");

        this.targetUrl = `/${packageUrl}/chats/${params.chat}#/?noheader=yes`;
        this.requiredPackages = {}
        this.requiredPackages[packageName] = `${this.baseGitUrl}/${packageUrl}`;

        this.init(view);
    }
}
