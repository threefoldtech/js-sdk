
import { JetView } from "webix-jet";
import { health } from "../../services/health"

export default class JSXInfoView extends JetView {
    config() {
        return {
            gravity:1,
            view: "template",
            id: "js_info",
            css: "js_info",
            template: (obj) => {
                let ret = "";
                ret += `<div class="header_div" style="user-select: auto;"><img class="header_image" src="static/img/header.png" alt="..."></div>`
                ret += `<div><h3 class='threebot_name'><b>3bot name:</b> ${obj.threebot_name}</h3>
                        <p class='threebot_id'><b>3bot id:</b> ${obj.threebot_id}</p></div>`;
                ret += `<p class="js_version"><b>JS Version: </b>${obj.js_version}</p>`
                ret += `<b class='threebot_id'>Interface name: </b>${obj.interface_name}<br>
                        <b class='threebot_id'>IP: </b>${obj.ip}`
                return ret;
            }
        }
    }

    init() {
        const self = this;
        const js_info = {
            'threebot_name': "",
            'threebot_id': "",
            'js_version': 'alpha 0.2.0',
            'interface_name': "",
            'ip':""
        }

        health.getIdentity().then((data)=>{
            let identity = JSON.parse(data.json()).data
            js_info.threebot_name = identity.name
            js_info.threebot_id = identity.id
            $$("js_info").parse(js_info);
        }).catch((error)=>{
            console.log(error)
        })

        health.getNetworkInfo().then((data) => {
            let network = JSON.parse(data.json()).data
            js_info.interface_name = network[0]
            js_info.ip = network[1]
            $$("js_info").parse(js_info);
        }).catch((error)=>{
            console.log(error)
        });
    }
}
