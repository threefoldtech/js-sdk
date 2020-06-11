
import { BaseView } from './baseview'
import { solutions } from '../../services/deployedSolutions'

// TODO: Add chat link
const CHAT = ""

export default class DeployedUbuntuView extends BaseView {
    constructor(app, name) {
        
        super(app, name, CHAT, "ubuntu.png");
    }
}