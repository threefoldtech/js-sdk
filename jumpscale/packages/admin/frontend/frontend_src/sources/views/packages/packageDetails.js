import { JetView } from "webix-jet";

export default class PackageDetailsView extends JetView {
    config() {
        const info = {

            // TODO: update form according to new package info
            view: "form",
            id: "form",
            elementsConfig: { labelWidth: 120 },
            elements: [
                {
                    view: "text",
                    label: "ID",
                    name: "id",
                    readonly: true,
                },
                {
                    view: "text",
                    label: "Name",
                    name: "source_name",
                    readonly: true,
                },
                {
                    view: "text",
                    label: "Author",
                    name: "author",
                    readonly: true,
                },
                {
                    view: "text",
                    label: "Status",
                    name: "status",
                    readonly: true,
                },
                {
                    view: "textarea",
                    label: "Description",
                    height: 100,
                    name: "description",
                    readonly: true
                },
                {
                    view: "text",
                    label: "Version",
                    name: "version",
                    readonly: true
                },
                {
                    view: "text",
                    label: "install_kwargs",
                    name: "install_kwargs",
                    readonly: true
                },
                {
                    view: "text",
                    label: "frontend_args",
                    name: "frontend_args",
                    readonly: true
                },
                {
                    view: "text",
                    label: "Path",
                    name: "path",
                    readonly: true
                },
                {
                    view: "text",
                    label: "giturl",
                    name: "giturl",
                    readonly: true,
                }
            ]
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