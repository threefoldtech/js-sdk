import { JetView } from "webix-jet";
import { admin } from "../../services/admin";

export default class ExplorerView extends JetView {
    config() {

        return {
            localId: "explorer_form",
            view: "form",
            elements: [
                {
                    view: "richselect",
                    id: "explorers_list",
                    label: "Explorer",
                    labelWidth: 150,
                    value: "testnet",
                    yCount: 2,
                    options: [
                        { id: "testnet", value: "Test Net" },
                        { id: "main", value: "Main" },
                    ]
                },
                {
                    localId: "explorer_url",
                    view: "text",
                    readonly: true,
                    label: "Explorer url",
                    labelWidth: 150,
                },
            ]
        }

    }

    init() {
        var self = this;

        self.form = self.$$('explorer_form');
        webix.extend(self.form, webix.ProgressBar);

        self.explorerList = self.$$('explorers_list');
        self.explorerUrl = self.$$('explorer_url');

        admin.getExplorer().then((data) => {
            const explorer = JSON.parse(data.json()).data;
            self.explorerList.setValue(explorer.type);
            self.explorerUrl.setValue(explorer.url);
        }).catch((error) => {
            console.log(error);
            this.webix.message({ type: "error", text: "Error on getting current explorer"})
        });

        self.explorerList.attachEvent("onChange", (newValue, oldValue) => {
            admin.setExplorer(newValue.toLowerCase()).then((data) => {
                const response = JSON.parse(data.json()).data;
                self.explorerUrl.setValue(response.url);
            }).catch((error) => {
                self.explorerList.setValue(oldValue);
                this.webix.message({ type: "error", text: "Error on switching explorer"})
            });
        });
    }
}
