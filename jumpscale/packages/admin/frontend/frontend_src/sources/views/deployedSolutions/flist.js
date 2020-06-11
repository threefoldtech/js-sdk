import { BaseView } from './baseview'
import { solutions } from '../../services/deployedSolutions'

const CHAT = "/tfgrid_solutions/chats/flist_deploy/"

export default class DeployedFlistView extends BaseView {
    constructor(app, name) {
        super(app, name, CHAT, "flist.png");
    }
}


