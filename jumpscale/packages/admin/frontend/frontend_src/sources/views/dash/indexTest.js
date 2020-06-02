import { JetView } from "webix-jet";

// #4572b5 blue
// #7db78e green
// #c9c9c9 selver

export default class TopView extends JetView {
    config() {
        const wide = {
            type: "clean",
            id: "dash",
            rows: [{
                    $subview: "dash.solutions_cards"
                },
                {
                    $subview: "dash.threebot_cards"
                },
                {
                    gravity: 7.1,
                    cols: [{
                            rows: [{
                                    gravity: 2,
                                    cols: [{
                                            $subview: "dash.jsx_info"
                                        },
                                        {
                                            $subview: "dash.processes_chart"
                                        },
                                    ]
                                },
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

        const small = {
            type: "clean",
            id: "dash",
            rows: [{
                    $subview: "dash.solutions_cards"
                },
                {
                    $subview: "dash.threebot_cards"
                },
                {
                    gravity: 7.1,
                    rows: [{
                            gravity: 2,
                            cols: [{
                                    $subview: "dash.jsx_info"
                                },
                                {
                                    $subview: "dash.processes_chart"
                                },
                            ]
                        },
                        {
                            $subview: "dash.graph_chart"
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

        switch (this.app.config.size) {
            case "small":
                console.log("small small small")
                return small
            default :
            console.log("wide wide wide ")
                return wide
        }
    }

    init() {
        const self = this
        const size = () => document.body.offsetWidth > 1000 ? "wide" : "small";

        this.app.config.size = size();
        webix.event(window, "resize", function() {
            var newSize = size();
            if (newSize != this.app.config.size) {
                this.app.config.size = newSize;
                console.log("new size: ", this.app.config.size)
                self.$$("dash").resize();
            }
        });

    }
}