import { BaseView } from './baseview'
import { solutions } from '../../services/deployedSolutions'

const CHAT = "/tfgrid_solutions/chats/gitea_deploy/"

export default class DeployedGiteaView extends BaseView {
    constructor(app, name) {
        super(app, name, CHAT, "gitea.png");
    }
}