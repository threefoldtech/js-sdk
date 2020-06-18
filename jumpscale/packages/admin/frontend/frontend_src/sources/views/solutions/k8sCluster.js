import { BaseView } from './baseview'
import { solutions } from '../../services/solutions'

const CHAT = "solutions.chatflow?package=tfgrid_solutions&chat=kubernetes_deploy"

export default class DeployedK8sClustersView extends BaseView {
    constructor(app, name) {
        super(app, name, CHAT, "k8s.png");
    }

    init(view) {
        super.init(view)
        let self = this
        self.parseData = []
        solutions.listSolution('Kubernetes').then((data) => {
            const solutions = JSON.parse(data.json()).data
            for (let i = 0; i < solutions.length; i++) {
                const solution = solutions[i];
                let master_ips = new Set();
                let slaves_ips = new Set()
                let dict = JSON.parse(solution.form_info)
                let reservation = solution.reservation
                let nodes = reservation.data_reservation.kubernetes
                for (let i = 0; i < nodes.length; i++) {
                    const node = nodes[i];
                    if(node.master_ips.length === 0)
                        master_ips.add(node.ipaddress)
                    else
                        slaves_ips.add(node.ipaddress)
                }
                dict['Master IPs'] = Array.from(master_ips).join('<br>')
                dict['Slaves IPs'] = Array.from(slaves_ips).join('<br>')
                dict.id = reservation.id
                dict._type = "Kubernetes"
                dict._name = dict['Solution name'].length > self.maxTitleLength ?
                    dict['Solution name'].substring(0, self.maxTitleLength) + '...' : dict['Solution name'];
                dict._ip = Array.from(master_ips).join('<br>')

                delete dict['IP Address']
                delete dict['chatflow']

                self.parseData.push(dict)
            }
            self.solutionlist.parse(self.parseData);
            self.solutionlist.showProgress({hide: true});
        });
    }
}
