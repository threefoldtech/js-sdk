import { BaseView } from './baseview'
import { solutions } from '../../services/deployedSolutions'

const CHAT = "/tfgrid_solutions/chats/domain_delegation/"

export default class DeployedDomainDelegationView extends BaseView {
    constructor(app, name) {
        super(app, name, CHAT, "domain.png");
    }    
}
