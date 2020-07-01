import { JetView } from "webix-jet";
import SolutionDetailsView from './SolutionDetails'

export class BaseView extends JetView {
    constructor(app, name, chat, logo) {
        super(app, name);
        this.logo = logo || "3bot.png";
        this.chat = chat;
    }
    config() {

        const logo = {
            view: "template",
            template: `<img class="deployed-solution-icon" src="static/img/${this.logo}">`,
            css: 'deployed-solution-logo-view',
            align: "center",
            borderless: true,
            height: 150
        }

        const view = {
            localId: "solutionMenu",
            view: "dataview",
            id: "solutionlist",
            data: this.data,
            width: 930,
            select: 1,
            css: "solutions-list",
            type: {
                width: 300,
                height: 100,
                template: "<div class='overall'><div class='title'>#_name#</div><div class='ip'>#_ip# </div> </div>"
            }
        }

        return {
            type: "space",
            rows:
                [
                    logo,
                    {
                        cols: [{}, {
                            view: "button",
                            id: "btnAddNew",
                            value: "Create New",
                            width:170,
                            height:70,
                            css: "webix_primary btnCreateNew",
                            click: function () {
                                this.$scope.show(this.$scope.chat)
                            }
                        }, {}]
                    },
                    { cols: [{}, view, {}] }
                ]
        };
    }

    init(view) {
        let self = this;
        self.solutionlist = $$("solutionlist")
        self.maxTitleLength = 20;
        webix.extend(self.solutionlist, webix.ProgressBar);
        self.solutionlist.showProgress({
            type: "icon",
            hide: false
        });
        self.SolutionDetailsView = self.ui(SolutionDetailsView)

        self.solutionlist.addCss(self.solutionlist.getFirstId(), 'createnewdiv')
        self.solutionlist.attachEvent("onItemClick", function (id) {
                let ret = self.parseData.find(solution => solution.id == id)
                let filtered = Object.assign({}, ret);
                let type =  filtered._type;
                for (let i = 0; i < Object.keys(filtered).length; i++) {
                    const key = Object.keys(filtered)[i];
                    if (key[0] === '_') {
                        delete filtered[key];
                        i--;
                    }
                }
                filtered['Reservation id'] = filtered.id
                delete filtered['id']
                self.SolutionDetailsView.showInfo(filtered,type)
        });
    }
}
