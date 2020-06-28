import { JetView } from "webix-jet";

// #4572b5 blue
// #7db78e green
// #c9c9c9 selver

export default class TopView extends JetView {
    config() {
        return {
            type:"clean",
            rows: [{
                    $subview: "dash.solutionsCards"
                },
                {
                    $subview: "dash.threebotCards"
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
                                        $subview: "dash.jsxInfo"
                                    },
                                    {
                                        $subview: "dash.processesChart"
                                    },
                                ]},
                                {
                                    $subview: "dash.graphChart"
                                }
                            ]
                        },
                        {
                            $subview: "dash.processesTable"
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
