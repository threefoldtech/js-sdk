import { BaseView } from './baseview'
import { solutions } from '../../services/deployedSolutions'

const CHAT = "/tfgrid_solutions/chats/minio_deploy/"

export default class DeployedMinioView extends BaseView {
    constructor(app, name) {
        super(app, name, CHAT, "minio.png");
    }
}

