import { JetView } from "webix-jet";

import { wallet } from "../../services/wallet";

export default class WalletImportView extends JetView {
    config() {
        const info = {
            view: "form",
            id: "import_form",
            elementsConfig: { labelWidth: 200 },
            elements: [{
                    view: "text",
                    label: "Name",
                    name: "name",
                    placeholder: "Wallet name"
                },
                {
                    view: "text",
                    label: "Secret",
                    name: "secret",
                    placeholder: "Wallet secret"
                },
                {
                    view: "select",
                    label: "Network Type",
                    value: "network",
                    name: "network",
                    options: [
                        { "id": "STD", "value": "STD" },
                        { "id": "TEST", "value": "TEST" }
                    ]
                }
            ]
        };

        return {
            view: "window",
            id: "popupWindow",
            head: "Import wallet",
            modal: true,
            width: window.innerWidth * .8,
            height: window.innerHeight * .8,
            position: "center",
            body: {
                rows: [
                    info,
                    {
                        cols: [{
                            view: "button",
                            value: "Close",
                            css: "webix_secondary",
                            click: function() {
                                this.getTopParentView().hide();
                            }
                        }, {
                            view: "button",
                            value: "OK",
                            css: "webix_primary",
                            click: function() {
                                var name = $$('import_form').getValues().name
                                var secret = $$('import_form').getValues().secret
                                var network = $$('import_form').getValues().network
                                this.$scope.importWallet(name, secret, network);
                            }
                        }]
                    }
                ]
            }
        }
    }

    init() {
        this.form = $$("import_form");
        $$("popupWindow").attachEvent("onKeyPress", function(code, e) {
            if (code == 27) {
                this.getTopParentView().hide();
            }
        });
    }

    showForm() {
        this.getRoot().show();
    }

    importWallet(name, secret, network) {
        webix.extend(this.form, webix.ProgressBar);
        this.form.showProgress({
            type: "icon",
            hide: false
        });
        wallet.importWallet(name, secret, network).then(data => {
            webix.message({ type: "success", text: "Wallet imported successfully" });
            this.form.showProgress({ hide: true });
            this.form.clear();
            this.form.getTopParentView().hide();
            this.app.refresh()
        }).catch(error => {
            webix.message({ type: "error", text: "Could not import wallet" });
            this.form.showProgress({ hide: true });
            this.form.clear();
            this.form.getTopParentView().hide();
            this.app.refresh()
        });
    }
}
