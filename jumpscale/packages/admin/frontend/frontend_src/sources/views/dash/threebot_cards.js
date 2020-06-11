import { JetView } from "webix-jet";
import { admin } from "../../services/admin";
import { alerts } from "../../services/alerts";
import { health } from "../../services/health";

export default class ThreebotCardsView extends JetView {
    config() {
        this.minItemWidth = 320;
        const initCount = Math.floor(document.documentElement.clientWidth / this.minItemWidth);

        return {
            gravity: 2.6,
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
                        return `<img class='threebot_card_icon' src='${obj.icon}'>`;
                    else return `<p>unavailable</p>`
                },
                title: obj => {
                    if (obj.title)
                        return `<h2 class='threebot_card_title'>${obj.title}</h2>`;
                    else return `<p>unavailable</p>`
                },
                info: obj => {
                    if (obj.info)
                        return `<div class='threebot_card_info'>${obj.info}</div>`;
                    else return `<p>unavailable</p>`
                }
            }
        }
    }

    init() {
        const threebot_cards = this.$$("threebot_cards");

        let threebot_card_data = [
            { "id": 1, "title": "Health checks", "info": "All izz well", "icon": "static/img/health.png" },
            { "id": 2, "title": "Errors", "info": "", "icon": "static/img/error.png" },
            { "id": 3, "title": "Memory usage", "info": "", "icon": "static/img/memory.png" },
            {'id': 4,'title': 'Explorer','info': "",'icon': 'static/img/explorer.png'}
        ];

        alerts.count().then((data) => {
            const alertCount = JSON.parse(data.json()).data;
            console.log("dsdsd",alertCount)
            threebot_card_data[1].info = `<a class="threebot_card_info" href="#!/main/alerts">Find ${alertCount} alerts</a>`;
            threebot_cards.parse(threebot_card_data);
        })

        health.getMemoryUsage().then((data) => {
            let memoryUsage = JSON.parse(data.json()).data
            threebot_card_data[2].info = `<p><b>Total: </b>${memoryUsage.total} GB</p><p><b>Used: </b>${memoryUsage.used} GB</p><p><b>Percentage: </b>${memoryUsage.percent}%</p>`;
        });

        admin.getExplorer().then((data) => {
            const explorer = JSON.parse(data.json());
            let explorer_url = explorer.url;
            threebot_card_data[3].info = explorer_url;
            threebot_cards.parse(threebot_card_data);
        })

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