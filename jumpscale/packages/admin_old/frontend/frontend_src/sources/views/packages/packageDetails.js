import { JetView } from "webix-jet";

export default class PackageDetailsView extends JetView {
    config() {
        const info = {
            view: "form",
            id: "form",
            elementsConfig: { labelWidth: 120 },
            elements: [
                {
                    view: "text",
                    label: "Name",
                    name: "name",
                    readonly: true,
                },
                {
                    view: "text",
                    label: "Path",
                    name: "path",
                    readonly: true
                },
                {
                    view: "text",
                    label: "Git url",
                    name: "giturl",
                    readonly: true,
                },
                {
                    view: "text",
                    label: "Installed",
                    name: "installed",
                    readonly: true,
                },
            ],
        };

        return {
            view: "window",
            head: "Package Details",
            modal: true,
            width: window.innerWidth * .8,
            height: window.innerHeight * .8,
            position: "center",
            body: {
                rows: [
                    info,
                    {
                        view: "button",
                        value: "OK",
                        css: "webix_primary",
                        click: function () {
                            this.getTopParentView().hide();
                        }
                    }
                ]
            }
        }
    }

    showPackageDetails(data) {
        this.form.parse(data)
        this.getRoot().show();
    }

    init() {
        this.form = $$("form");
    }
}
