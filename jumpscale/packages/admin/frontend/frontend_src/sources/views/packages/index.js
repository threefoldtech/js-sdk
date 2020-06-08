import { JetView } from "webix-jet";

import { ErrorView } from "../errors/dialog";
import { packages } from "../../services/packages";
import PackageDetailsView from "./packageDetails"

// const UNKNOWN_STATUS = 'Unknown';

// const PACKAGE_STATES = [
//     {
//         name: "Init",
//         actions: []
//     },
//     {
//         name: "Config",
//         actions: ['install'],
//     },
//     {
//         name: "Installed",
//         actions: ['start']
//     },
//     {
//         name: "Running",
//         actions: ["stop"]
//     },
//     {
//         name: "Halted",
//         actions: ["start", "disable"]
//     },
//     {
//         name: "Disabled",
//         actions: ["enable"]
//     },
//     {
//         name: "Error",
//         actions: ['install']
//     }
// ];

export default class PackagesView extends JetView {
    config() {
        const grid = {
            rows: [{
                //Header
                view: "template",
                type: "header",
                template: "Packages",
            },
            { //adding Package
                cols: [{
                    //selector
                    view: "select",
                    id: 'method_selector',
                    options: ["Path", "Giturl"],
                    width: 100
                },
                //text area
                {
                    view: "text",
                    id: 'package_path',
                    inputAlign: "left",
                },
                //submit button
                {
                    view: "button",
                    id: "add_package_button",
                    value: "Add package",
                    autowidth: true,
                    type: "",
                }
                ]
            },
            { //DataTable
                
                // TODO: update table according to new package info
                view: "datatable",
                id: "packages_table",
                resizeColumn: true,
                type: {
                    height: 200,
                },
                scroll: "xy",
                autoConfig: true,
                view: "datatable",
                select: true,
                css: "webix_header_border webix_data_border",
                onContext: {},
                columns: [{
                    id: "index",
                    header: "#",
                    sort: "int",
                    autowidth: true,
                },
                // {
                //     id: "author",
                //     header: ["Author", {
                //         content: "selectFilter"
                //     }],
                //     sort: "string",
                //     width: 200
                // }, {
                {
                    id: "name",
                    header: ["Name", {
                        content: "textFilter"
                    }],
                    sort: "string",
                    width: 200
                },
                // {
                //     id: "status",
                //     header: "Status",
                //     sort: "string",
                //     format: (value) => {
                //         const status = PACKAGE_STATES[value];
                //         return status && status.name || UNKNOWN_STATUS;
                //     },
                // }, {
                {
                    id: "path",
                    header: "Path",
                    sort: "string",
                    width: 700
                }
                ],
                scheme: {
                    $init: function (obj) {
                        obj.index = this.count();
                    }
                }
            }
            ]
        };
        return grid;
    }

    showError(message) {
        this.errorView.showError(message);
    }

    handleResult(promise, callback) {
        this.packageTable.showProgress({ hide: false });

        promise.then((data) => {
            const packageItem = JSON.parse(data.json()).package;
            if (callback instanceof Function) {
                callback(packageItem);
            }

            webix.message({
                type: "success",
                text: "The operation has beed done successfully"
            });

            this.packageTable.showProgress({ hide: true });
        }).catch(error => {
            this.showError("Error has happened during this operation: " + error.response, "Error");
            this.packageTable.showProgress({ hide: true });
        })
    }

    addPackage(path, gitUrl, itemId) {
        this.handleResult(packages.add(path, gitUrl), (item) => {
            if (itemId) {
                this.packageTable.updateItem(itemId, item);
            } else {
                this.packageTable.add(item);
            }
        });
    }

    deletePackage(packageName, itemId) {
        this.handleResult(packages.delete(packageName), () => {
            this.packageTable.remove(itemId)
        });
    }

    startPackage(packageName, itemId) {
        this.handleResult(packages.start(packageName), (item) => {
            this.packageTable.updateItem(itemId, item);
        });
    }

    stopPackage(packageName, itemId) {
        this.handleResult(packages.stop(packageName), (item) => {
            this.packageTable.updateItem(itemId, item);
        });
    }

    // enablePackage(packageName, itemId) {
    //     this.handleResult(packages.enable(packageName), (item) => {
    //         this.packageTable.updateItem(itemId, item);
    //     });
    // }

    // disablePackage(packageName, itemId) {
    //     this.handleResult(packages.disable(packageName), (item) => {
    //         this.packageTable.updateItem(itemId, item);
    //     });
    // }

    loadPackages() {
        packages.list().then(data => {
            this.packageTable.parse(JSON.parse(data.json()));
        });
    }

    init(view) {
        const self = this;

        self.errorView = this.ui(ErrorView);
        self.packageDetailsView = self.ui(PackageDetailsView);

        // TODO: Add checks for required packages
        // self._requiredpackages = ["zerobot.base", "zerobot.webinterface", "zerobot.admin"]

        const menu = webix.ui({
            view: "contextmenu",
            id: "packages_cm"
        });

        this.packageTable = this.$$("packages_table");
        webix.extend(this.packageTable, webix.ProgressBar);

        function checkAction(action, selectedItemId) {
            const item = self.packageTable.getItem(selectedItemId);
            if (item) {
                let itemId = item.id;
                let packageName = item.name;

                if (action == 'install') {
                    self.addPackage(item.path, null, itemId);
                } else if (action == 'delete') {
                    webix.confirm({
                        title: "Delete Package",
                        ok: "Yes",
                        text: `Are you sure you want to delete ${packageName}?`,
                        cancel: "No",
                    }).then(() => {
                        self.deletePackage(packageName, itemId)
                    });
                    //
                } else if (action == 'start') {
                    self.startPackage(packageName, itemId)
                } else if (action == 'stop') {
                    self.stopPackage(packageName, itemId)
                }// } else if (action == 'disable') {
                //     self.disablePackage(packageName, itemId)
                // } else if (action == 'enable') {
                //     self.enablePackage(packageName, itemId)
                // }
            } else {
                webix.message("you have to select a package")
            }
        }

        $$("add_package_button").attachEvent("onItemClick", function (id) {
            let packageLocation = $$("package_path").getValue()
            if (packageLocation == "") {
                alert("please enter package location")
            } else {
                let packageMethod = $$("method_selector").getValue()
                let gitUrl = null;
                let path = null;
                if (packageMethod == "Giturl") {
                    gitUrl = packageLocation
                } else if (packageMethod == "Path") {
                    path = packageLocation
                } else {
                    alert("something went wrong during selecting the package method")
                }
                self.addPackage(path, gitUrl)
            }
        });

        $$("packages_cm").attachEvent("onMenuItemClick", function (id) {
            checkAction(id, self.packageTable.getSelectedId());
        });


        webix.event(self.packageTable.$view, "contextmenu", function (e /*MouseEvent*/) {
            const pos = self.packageTable.locate(e);
            if (pos) {
                const item = self.packageTable.getItem(pos.row);

                // TODO: Add checks for required packages
                // if (self._requiredpackages.includes(item.name)) {
                //     webix.message({ type: "error", text: `${item.name} is required package` });
                //     return
                // }
                // const actions = [...PACKAGE_STATES[item.status].actions, 'delete'];
                const actions = ['start', 'stop', 'delete']
                menu.clearAll();
                menu.parse(actions);
                menu.show(e);
            }
            return webix.html.preventEvent(e);
        })

        self.loadPackages();

        // self.packageTable.attachEvent("onItemDblClick", function () {
        //     let id = self.packageTable.getSelectedId()
        //     let item = self.packageTable.getItem(id)
        //     console.log(item)
        //     let packageData = {
        //         'source_name': item['source_name'],
        //         'id': item['id'],
        //         'status': PACKAGE_STATES[item['status']] ?
        //             PACKAGE_STATES[item['status']].name :
        //             UNKNOWN_STATUS,
        //         'author': item['source']['threebot'],
        //         'description': item['source']['description'],
        //         'version': item['source']['version'],
        //         'install_kwargs': JSON.stringify(item['install_kwargs']),
        //         'frontend_args': JSON.stringify(item['frontend_args']),
        //         'path': item['path'],
        //         'giturl': item['giturl']
        //     }
        //     self.packageDetailsView.showPackageDetails(packageData);
        // });
    }
}
