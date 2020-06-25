import { JetView } from "webix-jet";
import { health } from "../../services/health"

const colorsDataset = [{
        color: "#36ee6d"
    },
    {
        color: "#367fee"
    },
    {
        color: "#36d3ee"
    },
    {
        color: "#a9ee36"
    },
    {
        color: "#eeea36"
    },
    {
        color: "#ee9e36"
    },
    {
        color: "#f55154"
    }
];

export default class ProcessesChartView extends JetView {
    config() {
        return {
            css: "processes_chart_div",
            padding: 10,
            gravity:1.3,
            rows: [{
                    template: "<div style='text-align:center;'><h4>Running processes memory usage (RSS) in MB<h4/></div>",
                    height: 40,
                    // borderless: true,
                },
                {
                    padding: 40,
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
                }
            ]
        }
    }

    init() {
        const processesChart = this.$$("processes_chart");

        var chartData = []

        health.getMemoryUsage().then((data) => {
            let memoryData = JSON.parse(data.json()).data
            processesChart.define("legend", {
                layout: "x",
                values: [{
                        text: `<b>Total memory: </b>${memoryData.total}GB`
                    },
                    {
                        text: `<b>Usage: </b>${memoryData.percent}%`
                    }
                ]
            })
            processesChart.refresh()
        });

        health.getRunningProcesses().then((data) => {
            let processesData = {};
            for (let i = 0; i < JSON.parse(data.json()).data.length; i++) {
                const process = JSON.parse(data.json()).data[i];
                if(process.name in processesData){
                    processesData[process.name] += process.rss;
                }else{
                    processesData[process.name] = process.rss;
                }
            }
            let colorNo = 7
            for ( let process in processesData) {
                var temp = {
                    "color": colorsDataset[--colorNo].color,
                    "name": process,
                    "rss": Math.ceil(processesData[process]),
                }
                chartData.push(temp)

                //Break when there is no more colors
                if (!colorNo)
                break;
            }

            processesChart.parse({
                data: chartData,
            });
        });


    }
}
