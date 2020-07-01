import { JetView } from "webix-jet";

import AdminsView from "./admins";
import ExplorerView from "./explorer";

export default class SettingsView extends JetView {
    config() {
        return {
            type:"clean",
            rows: [
                {
                    view: "template",
                    template: "Explorer",
                    type:"header",
                    css:"settings_header",
                }, ExplorerView,
                {
                    cols:[
                    {
                        gravity:5,
                        view: "template",
                        template: "Admins",
                        type:"header",
                        css:"settings_header",
                    },{
                        localId: "add_admin",
                        view: "button",
                        value: "Add new administrator",
                        click: function () {
                            this.$scope.adminsView.addAdmin()
                        },
                    }]
                }
                , AdminsView]
        };
    }

    init () {
        this.adminsView = this.ui(AdminsView);
    }
}
