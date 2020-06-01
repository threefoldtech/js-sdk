
import { JetView } from "webix-jet";

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
                    autowidth: true,
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
                },
                {
                    id: "pid",
                    header: "PID",
                    sort: "int"
                },
                {
                    id: "username",
                    header: "Username",
                    sort: "string"
                },
                {
                    id: "rss",
                    header: "Memory Usage",
                    sort: "int",
                    format: function(value) {
                        return Math.ceil(value)
                    }
                },
                {
                    id: "port",
                    header: "Port",
                    sort: "string"
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

        const processes_data = [{
                "name": "P1",
                "pid": "123",
                "username": "p1",
                "rss": "15",
                "port": "1234"
            },
            {
                "name": "P2",
                "pid": "23",
                "username": "p2",
                "rss": "20",
                "port": "1434"
            },
            {
                "name": "P3",
                "pid": "151",
                "username": "p3",
                "rss": "10",
                "port": "5212"
            },
            {
                "name": "P4",
                "pid": "11",
                "username": "p4",
                "rss": "14",
                "port": "2367"
            },
            {
                "name": "P5",
                "pid": "2415",
                "username": "p5",
                "rss": "9",
                "port": "3456"
            },
            {
                "name": "P6",
                "pid": "7452",
                "username": "p6",
                "rss": "23",
                "port": "8563"
            },
            {
                "name": "P7",
                "pid": "1244",
                "username": "p7",
                "rss": "50",
                "port": "3633"
            },
            {
                "name": "P8",
                "pid": "4",
                "username": "p8",
                "rss": "20",
                "port": "4122"
            },
            {
                "name": "P9",
                "pid": "455",
                "username": "p9",
                "rss": "3",
                "port": "2729"
            },
            {
                "name": "P5",
                "pid": "2415",
                "username": "p5",
                "rss": "9",
                "port": "3456"
            },
            {
                "name": "P7",
                "pid": "1244",
                "username": "p7",
                "rss": "50",
                "port": "3633"
            },
            {
                "name": "P3",
                "pid": "151",
                "username": "p3",
                "rss": "10",
                "port": "5212"
            },
            {
                "name": "P1",
                "pid": "123",
                "username": "p1",
                "rss": "15",
                "port": "1234"
            },
            {
                "name": "P7",
                "pid": "1244",
                "username": "p7",
                "rss": "50",
                "port": "3633"
            },
            {
                "name": "P7",
                "pid": "1244",
                "username": "p7",
                "rss": "50",
                "port": "3633"
            },
        ]
        processesTable.parse(processes_data);
    }
}
