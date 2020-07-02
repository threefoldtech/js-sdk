import { BaseView } from './baseview'
import { solutions } from '../../services/solutions'

const CHAT = "solutions.chatflow?package=tfgrid_solutions&chat=flist_deploy"

export default class DeployedFlistView extends BaseView {
    constructor(app, name) {
        super(app, name, CHAT, "flist.png");
    }

    init(view) {
        super.init(view)
        let self = this
        self.parseData = []
        solutions.listSolution('Flist').then((data) => {
            const solutions = JSON.parse(data.json()).data
            for (let i = 0; i < solutions.length; i++) {
                const solution = solutions[i];
                let dict = JSON.parse(solution.form_info)
                let reservation = solution.reservation
                if (!dict['Solution name'])     // for flists created by other solutions not flist chatflow
                    continue;
                if(dict['Interactive'] === 'YES'){
                    delete dict['Entry point']
                }
                dict.id = reservation.id
                dict._type = "Flist"
                dict._name = dict['Solution name'].length > self.maxTitleLength ?
                    dict['Solution name'].substring(0, self.maxTitleLength) + '...' : dict['Solution name'];
                dict._ip = dict['IP Address']

                delete dict['chatflow']
                self.parseData.push(dict)
            }
            self.solutionlist.parse(self.parseData)
            self.solutionlist.showProgress({hide: true});
        });
    }
}
