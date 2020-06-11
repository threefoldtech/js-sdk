import { JetView } from "webix-jet";

import WalletFormView from "./walletForm";
import WalletDetailsView from "./walletDetails";
import WalletImportView from "./importForm"
import { wallet } from "../../services/wallet";

export default class WalletManagerView extends JetView {
    config() {
        const wallets = {
            view: "datatable",
            id: "wallets_table",
            resizeColumn: true,
            select: true,
            multiselect: true,
            css: "webix_header_border webix_data_border",
            scroll: true,
            autoConfig: true,
            columns: [{
                id: "index",
                header: "#",
                sort: "int",
                autowidth: true,
            },
            {
                id: "name",
                header: ["Name"],
                sort: "string",
                autowidth: true,
                width: 140
            },
            {
                id: "address",
                header: ["Address"],
                sort: "string",
                autowidth: true,
                width: 'auto'
            }
            ],
            scheme: {
                $init: function (obj) {
                    obj.index = this.count();
                }
            }
        };

        const view = {
            cols: [
                {
                    view: "template",
                    type: "header", template: "Wallets",
                },
                {
                    view: "button",
                    id: "btn_create",
                    value: "Create Wallet",
                    css: "webix_secondary",
                    autowidth: true,
                    click: function () {
                        this.$scope.walletFormView.showForm()
                    }
                },
                {
                    view: "button",
                    id: "btn_import",
                    value: "Import Wallet",
                    css: "webix_secondary",
                    autowidth: true,
                    click: function () {
                        this.$scope.walletImportView.showForm()
                    }
                }
            ]
        };

        return {
            rows: [
                view,
                wallets
            ]
        }
    }

    init(view) {
        var self = this;

        self.wallets_table = $$("wallets_table");
        self.walletDetailsView = self.ui(WalletDetailsView)
        self.walletFormView = self.ui(WalletFormView);
        self.walletImportView = self.ui(WalletImportView);

        self.wallets_table.attachEvent("onItemDblClick", function () {
            webix.extend(self.wallets_table, webix.ProgressBar);
            self.wallets_table.showProgress({
                type: "icon",
                hide: false
            });

            let item = self.wallets_table.getSelectedItem()
            wallet.getWalletInfo(item.name).then(data => {
                let res = JSON.parse(data.json()).data
                var info = {
                    'name': item.name,
                    'address': res.address,
                    'secret': res.secret,
                    'balances': res.balances
                }
                self.walletDetailsView.showInfo(info)
                self.wallets_table.showProgress({ hide: true });
            }).catch(data => {
                console.log(data);
                self.wallets_table.showProgress({ hide: true });
                webix.message({ type: "error", text: "Failed to load wallet" });
            });
        });

        webix.ui({
            view: "contextmenu",
            id: "wallet_cm",
            data: ["delete"]
        }).attachTo(self.wallets_table);

        $$("wallet_cm").attachEvent("onMenuItemClick", function (id) {
            if (id == "delete") {
                let walletName = self.wallets_table.getSelectedItem().name
                webix.confirm({
                    title: "Delete Wallet",
                    ok: "Delete",
                    cancel: "No",
                    text: `Delete ${walletName} wallet?<br>Warning: You must save your wallet secret otherwise this action can't be undone`
                }).then(() => {

                    wallet.deleteWallet(walletName).then(() => {
                        self.refresh();
                        webix.message({ type: "success", text: `${walletName} wallet deleted successfully` });
                    }).catch(error => {
                        webix.message({ type: "error", text: "Could not delete wallet" });
                    })
                });
            }
        });
    }

    urlChange(view, url) {
        var self = this;

        self.wallets_table = $$("wallets_table");
        wallet.getWallets().then(data => {
            self.wallets_table.parse(JSON.parse(data.json()).data)
        });
    }
}
