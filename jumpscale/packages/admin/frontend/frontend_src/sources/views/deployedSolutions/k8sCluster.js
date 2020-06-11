import { BaseView } from './baseview'
import { solutions } from '../../services/deployedSolutions'

const CHAT = "/tfgrid_solutions/chats/kubernetes_deploy/"

export default class DeployedK8sClustersView extends BaseView {
    constructor(app, name) {
        super(app, name, CHAT, "k8s.png");
    }
}

