import { BaseView } from './baseview'
import { solutions } from '../../services/deployedSolutions'

const CHAT = "/tfgrid_solutions/chats/solution_expose/"

export default class DeployedSolutionExposeView extends BaseView {
    constructor(app, name) {
        super(app, name, CHAT, "wan.png");
    }
}


