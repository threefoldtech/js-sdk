import { BaseView } from './baseview'
import { solutions } from '../../services/solutions'

const CHAT = "solutions.chatflow?package=tfgrid_solutions&chat=domain_delegation"

export default class DeployedDomainDelegationView extends BaseView {
    constructor(app, name) {
        super(app, name, CHAT, "domain.png");
    }

    init(view) {
        super.init(view)
        let self = this
        self.parseData = []
        solutions.listSolution('DelegatedDomain').then((data) => {
            const solutions = JSON.parse(data.json()).data
            for (let i = 0; i < solutions.length; i++) {
                const solution = solutions[i];
                let dict = JSON.parse(solution.form_info)
                let reservation = solution.reservation
                dict['Expiration Provisioning'] = reservation.data_reservation.expiration_provisioning
                dict['Currencies'] = reservation.data_reservation.currencies
                dict.id = reservation.id
                dict._type = "DelegatedDomain"
                dict._name = dict["Domain"].length > self.maxTitleLength ?
                    dict["Domain"].substring(0, self.maxTitleLength) + '...' : dict["Domain"];
                dict._name = dict["Domain"]
                dict._ip = ""

                delete dict['rid']
                self.parseData.push(dict)
            }
            self.solutionlist.parse(self.parseData);
            self.solutionlist.showProgress({ hide: true });
        });
    }
}
