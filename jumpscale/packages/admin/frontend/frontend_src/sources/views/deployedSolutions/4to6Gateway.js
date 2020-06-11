import { BaseView } from './baseview'
import { solutions } from '../../services/deployedSolutions'

// TODO: Add chat link
const CHAT = ""

export default class Deployed4to6GatewayView extends BaseView {
    constructor(app, name) {
        super(app, name, CHAT, "ip.png");
    }
}


