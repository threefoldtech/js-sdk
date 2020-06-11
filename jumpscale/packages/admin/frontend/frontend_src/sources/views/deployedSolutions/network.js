import { BaseView } from './baseview'
import { solutions } from '../../services/deployedSolutions'

const CHAT = "/tfgrid_solutions/chats/network_deploy/"

export default class DeployedNetworkView extends BaseView {
    constructor(app, name) {
        super(app, name, CHAT, "network.png");
    }
}
