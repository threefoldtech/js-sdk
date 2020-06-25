import { JetView } from "webix-jet";
import { solutions } from '../../services/solutions';
import { admin } from "../../services/admin";
import OldSolutionDetailsView from './OldSolutionDetails'

const STATUS = ["DEPLOY", "DELETED"]
const SOLUTION_TYPE = ["network", "ubuntu", "flist", "minio", "kubernetes", "gitea", "monitoring", "delegated_domain", "exposed", "4to6gw","unknown"]

export default class DeployedView extends JetView {
    config() {
        const view = {
            rows: [{
                    cols: [{
                        id: "headerLabel",
                        view: "label",
                        label: "explorer",
                        borderless: true,
                    }, {
                        view: "button",
                        id: "btn_export_all",
                        value: "Export All",
                        align: 'right',
                        inputWidth: 150,
                        click: function() {
                            this.$scope.exportAll()
                        }
                    }]
                },
                {
                    view: "datatable",
                    id: "solutionsTable",
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
                            id: "id",
                            sort: "int",
                            width: 150,
                            header: "Reservation id",
                        },
                        {
                            id: "name",
                            header: ["Solution name", {
                                content: "textFilter"
                            }],
                            width: 150,
                            sort: "string"
                        },
                        {
                            id: "solution_type",
                            sort: "string",
                            width: 150,
                            header: [
                                "Solution type",
                                {
                                    content: "selectFilter",
                                    options: SOLUTION_TYPE
                                }
                            ],
                        },
                        {
                            id: "status",
                            sort: "string",
                            width: 150,
                            header: [
                                "Status",
                                {
                                    content: "selectFilter",
                                    options: STATUS
                                }
                            ],
                        },
                        {
                            id: "reservation_date",
                            width: 250,
                            header: "Reservation date",
                            sort: "string"
                        }
                    ],
                    autoConfig: true,
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

    init(view) {
        let self = this;
        self.table = $$("solutionsTable");
        self.header = $$("headerLabel")
        self.OldSolutionDetailsView = self.ui(OldSolutionDetailsView)

        webix.extend(self.table, webix.ProgressBar);
        self.table.showProgress({
            type: "icon",
            hide: false
        });
        admin.getExplorer().then(data => {
            let ret = `All reservation on : ${JSON.parse(data.json()).data.url}`
            self.header.config.label = ret;
            self.header.config.width = webix.html.getTextSize(ret).width + 10;
            self.header.resize();
        });
        solutions.listAllSolutions().then((data) => {
            const solutions = JSON.parse(data.json()).data
            self.table.parse(solutions);
            self.table.showProgress({ hide: true });
        })


        self.table.attachEvent("onItemClick", function (id) {
            let item = self.table.getSelectedItem()
            self.OldSolutionDetailsView.showInfo(item.form_info)
    });
    }
}
