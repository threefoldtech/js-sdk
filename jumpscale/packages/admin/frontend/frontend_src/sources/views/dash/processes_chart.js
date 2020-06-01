
import { JetView } from "webix-jet";

const colorsDataset = [{
    color: "#ee3639"
},
{
    color: "#ee9e36"
},
{
    color: "#eeea36"
},
{
    color: "#a9ee36"
},
{
    color: "#36d3ee"
},
{
    color: "#367fee"
},
{
    color: "#9b36ee"
}
];

export default class ProcessesChartView extends JetView {
    config() {
        return {
            css:"processes_chart_div",
            padding:10,
            rows: [{
                template: "<div style='text-align:center;'><h4>Running processes memory usage (RSS) in MB<h4/></div>",
                height: 40,
                // borderless: true,
            },
            {
                padding:40,
                // borderless: true,
                id: "processes_chart",
                view: "chart",
                responsive: true,
                css: "processes_chart",
                type: "pie",
                color: "#color#",
                value: "#rss#",
                label: "<h4>#name#</h4>",
                pieInnerText: "<h4>#rss#</h4>",
            }]
        }
    }

    init() {
        const processesChart = this.$$("processes_chart");

        var chartData = []
        const processes_data = {
            'processes_list': [{
                    'name': 'P1',
                    'rss': '60'
                },
                {
                    'name': 'P2',
                    'rss': '9'
                },
                {
                    'name': 'P3',
                    'rss': '11'
                },
                {
                    'name': 'P4',
                    'rss': '20'
                },
                {
                    'name': 'P5',
                    'rss': '5'
                }
            ],
            'memoryUsage': '50',
            'totalMemory': '100',
            'percent': '50',
        }


        processesChart.define("legend", {
            layout: "x",
            values: [{
                    text: `<b>Total memory: </b>${processes_data.totalMemory}GB`
                },
                {
                    text: `<b>Usage: </b>${processes_data.percent}%`
                }
            ]
        })
        processesChart.refresh()

        for (let i = 0; i < processes_data.processes_list.length; i++) {
            //Break when there is no more colors
            if (i == colorsDataset.length)
                break;

            var temp = {
                "color": colorsDataset[i].color,
                "name": processes_data.processes_list[i].name,
                "rss": Math.ceil(processes_data.processes_list[i].rss),
            }
            chartData.push(temp)
        }

        processesChart.parse({
            data: chartData,
        });
    }
}
