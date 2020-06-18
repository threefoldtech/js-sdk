
import { JetView } from "webix-jet";
import { health } from "../../services/health";

export default class ProcessesTableView extends JetView {
    config() {
        return {
            view: "datatable",
            id: "processes_table",
            resizeColumn: true,
            select: true,
            scroll: "xy",
            autowidth: true,
            css: "processes_table",
            columns: [{
                    id: "index",
                    header: "#",
                    sort: "int",
                    width:40,
                },
                {
                    id: "name",
                    header: [
                        "Process",
                        {
                            content: "textFilter"
                        },
                    ],
                    sort: "string",
                    // autowidth: true,
                    width:140,
                },
                {
                    id: "pid",
                    header: "PID",
                    sort: "int",
                    width:60,
                },
                {
                    id: "username",
                    header: "Username",
                    sort: "string"
                },
                {
                    id: "rss",
                    header: "Memory(MB)",
                    sort: "int",
                    width:100,
                    format: function(value) {
                        return Math.ceil(value)
                    }
                },
                {
                    id: "ports",
                    header: "Ports",
                    width:190,
                    format:function(value){
                        let ret = `<select name="ports" class= "compo_ports" id="cars">`
                        for (let i = 0; i < value.length; i++) {
                            const port = value[i];
                            ret += `<option value="${i}">${port.port} , ${port.status}</option> `
                        }
                        ret += `</select>`
                        return ret;
                    }
                }
            ],
            scheme: {
                $init: function(obj) {
                    obj.index = this.count();
                }
            }
        }
    }

    init() {
        const processesTable = this.$$("processes_table");
        health.getRunningProcesses().then((data) => {
            processesTable.parse(JSON.parse(data.json()).data);
        });
    }
}
