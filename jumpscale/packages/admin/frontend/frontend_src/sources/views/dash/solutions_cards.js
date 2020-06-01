
import { JetView } from "webix-jet";

export default class SolutionsCardsView extends JetView {
    config() {
        return {
            gravity:1,
            view: "dataview",
            id: "solution_cards",
            xCount: 6,
            select: false,
            scroll: false,
            css: "solution_cards",
            type: {
                width: "auto",
                height: "auto",
                type: "tiles",
                css: "solution_single_card",
                template: (obj, common) => {
                    return common.icon(obj) +
                        common.title(obj) +
                        common.count(obj) +
                        "<button class='add-icon mdi mdi-plus'></button>"
                },
                icon: obj => {
                    if (obj.icon)
                        return `<image class='solution_card_icon' src='${obj.icon}'>`;
                    else return `<p>unavailable</p>`
                },
                title: obj => {
                    if (obj.title)
                        return `<p class='solution_card_title'><b>${obj.title}</b></p>`;
                    else return `<p>unavailable</p>`
                },
                count: obj => {
                    if (obj.info)
                        return `<p class='solution_card_count'><b>${obj.info}</b></p>`;
                    else return `<p>unavailable</p>`
                }
            }
        }
    }

    init() {
        const solution_cards = this.$$("solution_cards");

        const solutions_data = [
            { "id": 1, "title": "Network", "info": 3, "icon": "static/img/network.png" },
            { "id": 2, "title": "Ubuntu", "info": 1, "icon": "static/img/ubuntu.png" },
            { "id": 3, "title": "Flist", "info": 2, "icon": "static/img/flist.png" },
            { "id": 4, "title": "Minio", "info": 2, "icon": "static/img/minio.png" },
            { "id": 5, "title": "Kubernetes", "info": 1, "icon": "static/img/k8s.png" },
            { "id": 6, "title": "Gitea", "info": 1, "icon": "static/img/gitea.png" }
        ];

        solution_cards.parse(solutions_data);
    }
}
