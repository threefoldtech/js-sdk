import { BaseView } from './baseview'
import { solutions } from '../../services/solutions'

const CHAT = "solutions.chatflow?package=tfgrid_solutions&chat=4to6gw"

export default class Deployed4to6GatewayView extends BaseView {
    constructor(app, name) {
        super(app, name, CHAT, "ip.png");
    }

    init(view) {
        super.init(view)
        let self = this
        self.parseData = []
        solutions.listSolution('FourToSixGw').then((data) => {
            const solutions = JSON.parse(data.json()).data
            for (let i = 0; i < solutions.length; i++) {
                const solution = solutions[i];
                let dict = JSON.parse(solution.form_info)
                let reservation = solution.reservation
                dict.id = reservation.id
                dict._name = solution.name.length > self.maxTitleLength ?
                    solution.name.substring(0, self.maxTitleLength) + '...' : solution.name
                dict._ip = ""
                self.parseData.push(dict)
            }
            self.solutionlist.parse(self.parseData)
            self.solutionlist.showProgress({ hide: true });
        });
    }
}
