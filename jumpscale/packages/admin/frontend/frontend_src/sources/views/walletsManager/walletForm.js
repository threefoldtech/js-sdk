import { JetView } from "webix-jet";
import { wallet } from "../../services/wallet";

export default class WalletFormView extends JetView {
    config() {
        const info = {
            view: "form",
            id: "form",
            elementsConfig: { labelWidth: 200 },
            elements: [{
                view: "text",
                label: "Name",
                name: "name",
                placeholder: "Wallet name"
            }]
        };

        return {
            view: "window",
            id: "popupWindow",
            head: "Create new wallet",
            modal: true,
            width: window.innerWidth * .8,
            height: window.innerHeight * .8,
            position: "center",
            body: {
                rows: [{
                        view: "template",
                        css: "wallet-warning",
                        height: 30,
                        template: "WARNING: YOU'RE RESPONSIBLE FOR KEEPING YOUR WALLET SECRET SAFE"
                    },
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
                                var wallet_name = $$('form').getValues().name
                                this.$scope.createWallet(wallet_name);
                            }
                        }]
                    }
                ]
            }
        }
    }

    init() {
        this.form = $$("form");
        $$("popupWindow").attachEvent("onKeyPress", function(code, e) {
            if (code == 27) {
                this.getTopParentView().hide();
            }
        });
    }

    showForm() {
        this.getRoot().show();
    }

    createWallet(name) {
        webix.extend(this.form, webix.ProgressBar);
        this.form.showProgress({
            type: "icon",
            hide: false
        });
        wallet.createWallet(name).then(data => {
            webix.message({ type: "success", text: "Wallet created successfully" });
            this.form.showProgress({ hide: true });
            this.form.getTopParentView().hide();
            this.app.refresh()
        }).catch(error => {
            webix.message({ type: "error", text: "Could not create wallet", expire: -1 });
            this.form.showProgress({ hide: true });
            this.form.getTopParentView().hide();
            this.app.refresh()
        });
    }
}
