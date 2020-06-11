import { BaseView } from './baseview'
import { solutions } from '../../services/deployedSolutions'

// TODO: Add chat link
const CHAT = ""

export default class DeployedK8sClustersView extends BaseView {
    constructor(app, name) {
        super(app, name, CHAT, "k8s.png");
    }
}

