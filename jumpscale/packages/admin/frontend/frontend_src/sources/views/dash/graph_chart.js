import { JetView } from "webix-jet";

export default class GraphChartView extends JetView {
    config() {
        var dataset = [
            { id: 1, sales: 0, date: "Fab 23, 2020" },
            { id: 2, sales: 0, date: "Mar 09, 2020" },
            { id: 3, sales: 0, date: "Mar 24, 2020" },
            { id: 1, sales: 0, date: "Apr 08, 2020" },
            { id: 2, sales: 0, date: "Apr 23, 2020" },
            { id: 3, sales: 0, date: "May 08, 2020" },
            { id: 4, sales: 0, date: "May 23, 2020" },
            { id: 5, sales: 0.1481, date: "Jun 07, 2020" },
            { id: 6, sales: 0.1481, date: "Jun 22, 2020" }
        ];

        return {
            rows: [{
                    view: "template",
                    css:"chart_label",
                    gravity:.2,
                    template: (obj) => {
                        let ret = "TFT to USD";
                        return ret;
                    }
                },
                {
                    view: "chart",
                    css: "graph_chart",
                    gravity: 1.1,
                    padding: 35,
                    type: "area",
                    value: "#sales#",
                    color: "#36abee",
                    alpha: 0.8,
                    xAxis: {
                        template: "'#date#"
                    },
                    yAxis: {
                        start: 0,
                        end: .5,
                        step: 0.1,
                        // template: function (obj) {
                        //     return obj % 20 ? "" : obj;
                        // }
                    },
                    tooltip: {
                        template: "#sales#"
                    },
                    data: dataset
                }
            ]
        }
    }

    init() {}
}
