
import { BaseView } from './baseview'
import { solutions } from '../../services/deployedSolutions'

const CHAT = "/tfgrid_solutions/chats/ubuntu_deploy/"

export default class DeployedUbuntuView extends BaseView {
    constructor(app, name) {
        
        super(app, name, CHAT, "ubuntu.png");
    }
}