import { JetView } from "webix-jet";
import { inputDialog } from "../../common/dialogs";
import { admin } from "../../services/admin"

export default class AdminsView extends JetView {
    config() {
        var self = this;

        return {
            localId: "admins_table",
            view: "datatable",
            scroll:false,
            columns: [{
                id: "name",
                width: 500,
                header: "Name",
                sort: "string",
            }, {
                template: function (obj) {
                    return "<span class='webix_icon mdi mdi-trash-can webix_danger delete_admin'></span>";
                }
            }],
            onClick: {
                delete_admin: function (e, id) {
                    this.$scope.deleteAdmin(id);
                },
            }
        }
    }

    addAdmin() {
        const self = this;

        inputDialog("Add admin", "3Bot name", "Add", (input) => {
            admin.add(input).then(() => {
                self.table.add({ name: input });
                self.app.refresh()
            }).catch((error) => {
                console.log(error);
            })
        });
    }

    deleteAdmin(itemId) {
        const self = this;

        const item = self.table.getItem(itemId);

        webix.confirm({
            title: "Delete admin",
            ok: "Yes",
            text: `Are you sure you want to delete "${item.name}"?`,
            cancel: "No",
        }).then(() => {
            admin.delete(item.name).then(() => {
                self.table.remove(itemId);
            }).catch((error) => {
                console.log(error);
            })
        });
    }

    init() {
        this.table = this.$$("admins_table");

        admin.list().then(data => {
            this.table.parse(JSON.parse(data.json()).data);
        });
    }
}
