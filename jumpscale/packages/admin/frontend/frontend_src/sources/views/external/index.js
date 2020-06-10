import { JetView } from "webix-jet";


// TODO: Add required packages

export class ExternalView extends JetView {
    constructor(app, name, targetUrl) {
        super(app, name);

        this.targetUrl = targetUrl || "/";
    }

    config() {
        const self = this;

        return {
            view: "iframe",
            localId: "iframe-external",
            on: {
                onAfterLoad: function () {
                    if (this.hideProgress) {
                        this.hideProgress();
                    }
                    this.enable();
                }
            }
        }
    }

    showIframe() {
        this.externalIframe.show();
        this.externalIframe.showProgress({ type: "icon" });
        this.externalIframe.load(this.targetUrl);
    }

    init(view) {
        this.externalIframe = this.$$("iframe-external");
        this.externalIframe.disable();
        webix.extend(this.externalIframe, webix.ProgressBar);

        this.showIframe();
    }
}
