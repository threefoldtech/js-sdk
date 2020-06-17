import { BaseView } from './baseview'
import { solutions } from '../../services/solutions'

const CHAT = "solutions.chatflow?package=tfgrid_solutions&chat=ubuntu_deploy"

export default class DeployedUbuntuView extends BaseView {
    constructor(app, name) {

        super(app, name, CHAT, "ubuntu.png");
    }

    init(view) {
        super.init(view)
        let self = this
        self.parseData = []
        solutions.listSolution('Ubuntu').then((data) => {
            const solutions = JSON.parse(data.json()).data
            for (let i = 0; i < solutions.length; i++) {
                const solution = solutions[i];
                console.log(solution)
                let dict = JSON.parse(solution.form_info)
                let reservation = solution.reservation
                dict.id = reservation.id
                dict._type = "Ubuntu"
                dict._name = dict['Solution name'].length > self.maxTitleLength ?
                    dict['Solution name'].substring(0, self.maxTitleLength) + '...' : dict['Solution name'];
                dict._ip = dict['IP Address']


                self.parseData.push(dict)
            }
            self.solutionlist.parse(self.parseData);
            self.solutionlist.showProgress({ hide: true });
        });
    }
}
