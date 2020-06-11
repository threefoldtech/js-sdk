import { BaseView } from './baseview'
import { solutions } from '../../services/deployedSolutions'

const CHAT = "/tfgrid_solutions/chats/4to6gw/"

export default class Deployed4to6GatewayView extends BaseView {
    constructor(app, name) {
        super(app, name, CHAT, "ip.png");
    }
}


