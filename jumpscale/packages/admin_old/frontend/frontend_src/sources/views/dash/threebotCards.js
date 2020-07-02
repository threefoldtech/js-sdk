import { JetView } from "webix-jet";
import { admin } from "../../services/admin";
import { alerts } from "../../services/alerts";
import { health } from "../../services/health";

export default class ThreebotCardsView extends JetView {
    config() {
        return {
            gravity: 2.6,
            view: "dataview",
            id: "threebot_cards",
            xCount: 4,
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

    async getAlertCount() {
        const request = await alerts.count();
        return JSON.parse(request.json()).data;
    }

    async getMemoryUsage() {
        const request = await health.getMemoryUsage();
        return JSON.parse(request.json()).data;
    }

    async getExplorer() {
        const request = await admin.getExplorer();
        const explorer = JSON.parse(request.json()).data;
        return explorer.url;
    }

    async fetchData() {
        const alertCount = await this.getAlertCount();
        const memoryUsage = await this.getMemoryUsage()
        const explorerUrl = await this.getExplorer();

        let threebot_card_data = [
            { "id": 1, "title": "Health checks", "info": "Tests OK ✅", "icon": "static/img/health.png" },
            { "id": 2, "title": "Errors", "info": "", "icon": "static/img/error.png" },
            { "id": 3, "title": "Memory usage", "info": "", "icon": "static/img/memory.png" },
            { "id": 4, "title": "Explorer", "info": "", "icon": "static/img/explorer.png" }
        ];

        threebot_card_data[1].info = alertCount ?
                                        `<a class="threebot_card_info red_label" href="#!/main/alerts">Found ${alertCount} alerts</a>` :
                                        `<a class="threebot_card_info" href="#!/main/alerts">No alerts</a>`;
        threebot_card_data[2].info = `<p><b>Total: </b>${memoryUsage.total} GB</p><p><b>Used: </b>${memoryUsage.used} GB</p><p><b>Percentage: </b>${memoryUsage.percent}%</p>`;
        threebot_card_data[3].info = explorerUrl;

        return threebot_card_data;
    };

    init() {
        const threebot_cards = this.$$("threebot_cards");

        this.fetchData().then((data) => {
            threebot_cards.parse(data);
        })
    }
}
