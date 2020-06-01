import { JetView } from "webix-jet";

// #4572b5 blue
// #7db78e green
// #c9c9c9 selver

export default class TopView extends JetView {
    config() {
        return {
            type:"clean",
            rows: [{
                    $subview: "dash.solutions_cards"
                },
                {
                    $subview: "dash.threebot_cards"
                },
                {
                    gravity:7.1,
                    cols: [
                        {
                            rows:[
                                {
                                    gravity:2,
                                    cols:
                                [
                                    {
                                        $subview: "dash.jsx_info"
                                    },
                                    {
                                        $subview: "dash.processes_chart"
                                    },
                                ]},
                                {
                                    $subview: "dash.graph_chart"
                                }
                            ]
                        },
                        {
                            $subview: "dash.processes_table"
                        }
                    ]
                },
                {
                    gravity: 0.5
                }
            ]
        };
    }
}
