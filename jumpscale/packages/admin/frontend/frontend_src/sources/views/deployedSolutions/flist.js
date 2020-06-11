import { BaseView } from './baseview'
import { solutions } from '../../services/deployedSolutions'

// TODO: Add chat link
const CHAT = ""

export default class DeployedFlistView extends BaseView {
    constructor(app, name) {
        super(app, name, CHAT, "flist.png");
    }
}


