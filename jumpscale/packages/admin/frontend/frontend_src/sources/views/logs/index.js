import { JetView } from "webix-jet";

import { dateFormatter } from "../../common/formatters";
import { LEVELS } from "../alerts/data";
import { createFilterOptions } from "../../common/filters";

import { logs } from "../../services/logs";

export default class LogsView extends JetView {
    config() {
        const view = {
            rows: [{
                    cols: [{
                            view: "template",
                            type: "header",
                            template: "Logs",
                        },
                        {
                            view: "combo",
                            id: "apps_combo",
                            placeholder: "Choose your application",
                            align: "right",
                            value: "init",
                            on: {
                                onChange: function(appName) {
                                    this.$scope.show(`/main/logs`)
                                    this.$scope.showFor(appName)
                                }
                            }
                        },
                        {
                            view: "button",
                            id: "btn_delete",
                            value: "Delete",
                            css: "webix_danger",
                            inputWidth: 120,
                            click: function() {
                                this.$scope.delete()
                            }
                        },
                        {
                            view: "button",
                            id: "btn_delete",
                            value: "Clear",
                            css: "webix_secondary",
                            inputWidth: 120,
                            click: function() {
                                this.$scope.delete()
                            }
                        },
                        {
                            batch:"default" 
                        },
                        {
                            view: "button",
                            id: "btn_delete_all",
                            value: "Delete All",
                            css: "webix_danger",
                            align: 'right',
                            inputWidth: 100,
                            click: function() {
                                this.$scope.delete_all()
                            }
                        },
                        { width: 20 }
                    ],
                },
                {
                    rows: [{
                            view: "datatable",
                            id: "applogs_table",
                            pager: "pager",
                            resizeColumn: true,
                            select: true,
                            multiselect: true,
                            css: "webix_header_border webix_data_border",
                            scroll: true,
                            autoConfig: true,
                            on: {
                                onAfterLoad: function() {
                                    this.sort("epoch", "des");
                                    this.markSorting("epoch", "des");
                                }
                            },

                            columns: [{
                                    id: "id",
                                    header: [
                                        "Log#",
                                        {
                                            content: "textFilter"
                                        },
                                    ],
                                    sort: "int",
                                    width: 50,
                                    autowidth: true,
                                },

                                {
                                    id: "filepath",
                                    header: [
                                        "Path",
                                        {
                                            content: "textFilter"
                                        },
                                    ],
                                    sort: "string",
                                    autowidth: true,
                                    width: 140
                                },

                                {
                                    id: "linenr",
                                    header: [
                                        "Line.nr",
                                        {
                                            content: "textFilter"
                                        },
                                    ],
                                    sort: "int",
                                    autowidth: true,
                                    width: 60
                                },

                                {
                                    id: "context",
                                    header: [
                                        "Context",
                                        {
                                            content: "textFilter"
                                        },
                                    ],
                                    sort: "string"
                                },
                                {
                                    id: "message",
                                    header: [
                                        "Message",
                                        {
                                            content: "textFilter"
                                        },
                                    ],
                                    sort: "string",
                                    width: 500,
                                    autowidth: true
                                },
                                {
                                    id: "level",
                                    header: [
                                        "Level",
                                        {
                                            content: "selectFilter",
                                            options: createFilterOptions(LEVELS)
                                        },
                                    ],
                                    sort: "int",
                                    format: (value) => LEVELS[value],
                                    width: 100
                                },
                                {
                                    id: "epoch",
                                    header: [
                                        "Time",
                                        {
                                            content: "textFilter"
                                        },
                                    ],
                                    sort: "date",
                                    format: dateFormatter,
                                    width: 130
                                },
                                {
                                    id: "processid",
                                    header: [
                                        "PID",
                                        {
                                            content: "textFilter"
                                        },
                                    ],
                                    sort: "int",
                                    width: 60
                                },
                                {
                                    id: "cat",
                                    header: [
                                        "Category",
                                        {
                                            content: "textFilter"
                                        },
                                    ],
                                    sort: "string",
                                    width: 80
                                },
                                {
                                    id: "data",
                                    header: [
                                        "Data",
                                        {
                                            content: "textFilter"
                                        },
                                    ],
                                    sort: "string"
                                }

                            ]
                        },
                        {
                            view: "pager",
                            id: "pager",
                            size: 100,
                            group: 20
                        }
                    ]
                }
            ]
        };

        return view;
    }

    fetch_logs(appname) {
        logs.listLogs(appname).then(data => {
            data = JSON.parse(data.json()).data;
            this.table.clearAll()
            this.table.showProgress({ hide: true });
            this.table.parse(data)
        });
    }

    init() {
        // this.use(plugins.ProgressBar, "progress");
        let self = this;
        self.table = $$("applogs_table");
        self.appsCombo = $$("apps_combo");

        webix.extend(self.table, webix.ProgressBar);
        webix.ready(function() {
            self.table.showProgress({
                hide: false
            });
            self.fetch_logs("init")        
        });

        logs.listApps().then(data => {
            self.appsCombo.define("options", JSON.parse(data.json()).data);
            self.appsCombo.render();
        });

    }

    urlChange(view, url) {
        const appName = url[0].params.appname,
        logId = url[0].params.logid;
        if (appName) {
            this.showFor(appName);
        }
    }

    showFor(appName) {
        this.table = $$("applogs_table");
        this.fetch_logs(appName)
    }

    delete() {
        let appname = $$("apps_combo").getValue();
        if (appname) {
            webix.confirm({
                title: "Delete logs",
                ok: "Delete",
                cancel: "No",
                text: `Delete ${appname} logs?`
            }).then(() => {
                logs.delete(appname).then(() => {
                    this.refresh();
                    webix.message({ type: "success", text: `${appname} logs deleted successfully` });
                }).catch(error => {
                    webix.message({ type: "error", text: "Could not delete logs" });
                })
            });
        } else {
            webix.message({ type: "error", text: "Please select app for delete" });
        }
    }

    delete_all() {
        webix.confirm({
            title: "Delete all logs",
            ok: "Delete",
            cancel: "No",
            text: `Delete all logs?`
        }).then(() => {
            logs.deleteAll().then(() => {
                this.refresh();
                webix.message({ type: "success", text: `All logs deleted successfully` });
            }).catch(error => {
                webix.message({ type: "error", text: "Could not delete logs" });
            })
        });
    }
}