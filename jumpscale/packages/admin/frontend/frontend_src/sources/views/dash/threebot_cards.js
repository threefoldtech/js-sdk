

import { JetView } from "webix-jet";

export default class ThreebotCardsView extends JetView {
    config() {
        this.minItemWidth = 320;
        const initCount = Math.floor(document.documentElement.clientWidth / this.minItemWidth);

        return {
            gravity:2.6,
            view: "dataview",
            id: "threebot_cards",
            xCount: (initCount > 4) ? 4 : 2,
            select: false,
            scroll: false,
            css: "threebot_cards",
            type: {
                width: "auto",
                height: 200,
                type: "tiles",
                template: (obj, common) => {
                    return common.icon(obj) +
                        common.title(obj) +
                        common.info(obj)
                },
                icon: obj => {
                    if (obj.icon)
                        return `<image class='threebot_card_icon' src='${obj.icon}'>`;
                    else return `<p>unavailable</p>`
                },
                title: obj => {
                    if (obj.title)
                        return `<h2 class='threebot_card_title'>${obj.title}</h2>`;
                    else return `<p>unavailable</p>`
                },
                info: obj => {
                    if (obj.info)
                        return `<p class='threebot_card_info'>${obj.info}</p>`;
                    else return `<p>unavailable</p>`
                }
            }
        }
    }

    init() {
        const threebot_cards = this.$$("threebot_cards");

        const threebot_card_data = [
            { "id": 1, "title": "Health checks", "info": "Automation", "icon": "static/img/health.png" },
            { "id": 2, "title": "Errors", "info": "Product Quality Assurance", "icon": "static/img/error.png" },
            { "id": 3, "title": "Memory usage", "info": "Management", "icon": "static/img/memory.png" },
            { "id": 4, "title": "Explorer", "info": "Test Execution Engine", "icon": "static/img/explorer.png" }
        ];

        threebot_cards.parse(threebot_card_data);

        this._winresize = webix.event(window, "resize", () => this.resizeDataview(this.minItemWidth));
    }

    resizeDataview(minItemWidth) {
        const elements = Math.floor(this.$$("threebot_cards").$width / minItemWidth);
        const count = (elements >= 4) ? 4 : 2;
        this.$$("threebot_cards").define("xCount", count);
        this.$$("threebot_cards").adjust();
        this.$$("threebot_cards").resize();
    }
}
