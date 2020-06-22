import { JetView } from "webix-jet";

import { ansiUp } from "../../common/colors";
import { LEVELS, MAX_MSG_LEN, STATES, TYPES } from "./data";
import { dateFormatter } from "../../common/formatters";
import { alerts } from "../../services/alerts";

import AlertView from "./alert";
import { createFilterOptions } from "../../common/filters";


export default class AlertsView extends JetView {
    config() {
        const view = {
            rows: [{
                    view: "button",
                    id: "btn_export_all",
                    value: "Export All",
                    align: 'right',
                    inputWidth: 150,
                    click: function() {
                        this.$scope.exportAll()
                    }
                },
                {
                    view: "datatable",
                    id: "alerts_table",
                    resizeColumn: true,
                    select: true,
                    multiselect: true,
                    scroll: "xy",
                    css: "webix_header_border webix_data_border",
                    columns: [{
                            id: "index",
                            header: "#",
                            sort: "int",
                            autowidth: true,
                        },
                        {
                            id: "type",
                            sort: "int",
                            width: 150,
                            header: [
                                "Type",
                                {
                                    content: "selectFilter",
                                    options: createFilterOptions(TYPES)
                                }
                            ],
                        },
                        {
                            id: "count",
                            header: "Count",
                            sort: "int"
                        },
                        {
                            id: "status",
                            sort: "int",
                            header: [
                                "Status",
                                {
                                    content: "selectFilter",
                                    options: createFilterOptions(STATES)
                                }
                            ],
                        },
                        {
                            id: "level",
                            sort: "int",
                            format: (value) => LEVELS[value],
                            header: [
                                "Level",
                                {
                                    content: "selectFilter",
                                    options: createFilterOptions(LEVELS)
                                }
                            ],
                        },
                        {
                            id: "cat",
                            header: [
                                "Category",
                                {
                                    content: "textFilter"
                                }
                            ],
                            sort: "string"
                        },
                        {
                            id: "first_occurrence",
                            header: "First time",
                            sort: "date",
                            format: dateFormatter,
                            width: 200
                        },
                        {
                            id: "last_occurrence",
                            header: "Last time",
                            sort: "date",
                            format: dateFormatter,
                            width: 200
                        },
                        {
                            id: "message",
                            header: [
                                "Message",
                                {
                                    content: "textFilter"
                                },
                            ],
                            sort: "str",
                            fillspace: true,
                            format: function(value) {
                                if (value.length > MAX_MSG_LEN) {
                                    value = value.substr(0, MAX_MSG_LEN) + '...';
                                }
                                return ansiUp.ansi_to_html(value);
                            }
                        },
                    ],
                    autoConfig: true,
                    // url:{
                    //     $proxy:true,
                    //     load: function(view, params){
                    //         let data = webix.ajax("/zerobot/alerta/actors/alerta/list_alerts");
                    //         return data;
                    //     },
                    // }
                    scheme: {
                        $init: function(obj) {
                            obj.index = this.count();
                        }
                    },
                },
                {
                    $subview: true,
                    popup: true
                }
            ]
        };

        return view;
    }

    deleteItem(objects) {
        var self = this;

        let items = [],
            ids = [],
            indexes = [];

        for (let obj of objects) {
            ids.push(obj.id);
            let item = self.table.getItem(obj.id);
            items.push(item)
            indexes.push(item.index);
        }

        webix.confirm({
            title: "Delete alerts",
            ok: "Yes",
            cancel: "No",
            text: `Delete alert item(s) of ${indexes.join(", ")}`
        }).then(() => {
            const identifiers = items.map((item) => item.identifier);
            self.table.showProgress({
                hide: false
            })
            alerts.delete(ids).then(() => {
                self.table.remove(ids)
                self.table.showProgress({
                    hide: true
                })
            });
        });
    }

    exportItem(objects) {
        var self = this;

        let items = []
        let indexes = []

        if (Array.isArray(objects)) {
            for (let obj of objects) {
                let item = self.table.getItem(obj.id);
                items.push(item)
                indexes.push(item.index);
            }
        } else {
            let item = self.table.getItem(objects.id);
            items.push(item)
            indexes.push(item.index);
        }

        webix.confirm({
            title: "Export alerts",
            ok: "Yes",
            cancel: "No",
            text: `Export alert item(s) of ${indexes.join(", ")}`
        }).then(() => {
            var blob = new Blob([webix.stringify(items)], { type: "application/json" });
            var d = new Date();
            webix.html.download(blob, `alerts_export_${d.toString()}.json`)
        });
    }

    exportAll() {
        var self = this;
        webix.confirm({
            title: "Export all alerts",
            ok: "Export",
            cancel: "No",
            text: `Export all alerts?`
        }).then(() => {
            let items = self.table.serialize()
            var blob = new Blob([webix.stringify(items)], { type: "application/json" });
            var d = new Date();
            webix.html.download(blob, `alerts_export_${d.toString()}.json`)
        });
    }

    viewItem(id) {
        this.alertView.showFor(this.table.getItem(id));
    }

    init() {
        // this.use(plugins.ProgressBar, "progress");
        var self = this;
        self.table = $$("alerts_table");
        self.alertView = self.ui(AlertView);

        webix.extend(self.table, webix.ProgressBar);
        webix.ready(function() {
            self.table.clearAll();
            self.table.showProgress({
                hide: false
            });
            alerts.list().then(data => {
                let alerts = JSON.parse(data.json()).data;
                self.table.parse(alerts);
            });
        });

        webix.ui({
            view: "contextmenu",
            id: "alerts_cm",
            data: ["View", "Delete", "Export"]
        }).attachTo(self.table);


        self.table.attachEvent("onItemDblClick", function() {
            self.viewItem(self.table.getSelectedId());
        });

        $$("alerts_cm").attachEvent("onMenuItemClick", function(id) {
            if (id == "Delete") {
                self.deleteItem(self.table.getSelectedId(true));
            } else if (id == "View") {
                self.viewItem(self.table.getSelectedId());
            } else if (id == "Export") {
                self.exportItem(self.table.getSelectedId());
            }
        });
    }
}
