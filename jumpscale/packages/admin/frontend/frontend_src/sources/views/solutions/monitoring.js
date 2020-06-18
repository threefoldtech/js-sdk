import { BaseView } from './baseview'
import { solutions } from '../../services/solutions'

const CHAT = "solutions.chatflow?package=tfgrid_solutions&chat=monitoring_deploy"

export default class DeployedMonitoringView extends BaseView {
    constructor(app, name) {
        super(app, name, CHAT, "monitoring.png");
    }

    init(view) {
        super.init(view)
        let self = this
        self.parseData = []
        solutions.listSolution('Monitoring').then((data) => {
            const solutions = JSON.parse(data.json()).data
            for (let i = 0; i < solutions.length; i++) {
                const solution = solutions[i];
                let dict = JSON.parse(solution.form_info)
                let reservation = solution.reservation
                dict.id = reservation.id
                dict._type = "Monitoring"
                dict._name = dict['Solution name'].length > self.maxTitleLength ?
                    dict['Solution name'].substring(0, self.maxTitleLength) + '...' : dict['Solution name'];
                dict._ip = ""

                delete dict['chatflow']
                self.parseData.push(dict)
            }
            self.solutionlist.parse(self.parseData)
            self.solutionlist.showProgress({hide: true});
        });
    }
}
