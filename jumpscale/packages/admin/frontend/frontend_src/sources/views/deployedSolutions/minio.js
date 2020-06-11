import { BaseView } from './baseview'
import { solutions } from '../../services/deployedSolutions'

// TODO: Add chat link
const CHAT = ""

export default class DeployedMinioView extends BaseView {
    constructor(app, name) {
        super(app, name, CHAT, "minio.png");
    }
}

