
import { JetView } from "webix-jet";
import { admin } from "../../services/admin"

export default class JSXInfoView extends JetView {
    config() {
        return {
            gravity:1,
            view: "template",
            id: "jsx_info",
            css: "jsx_info",
            template: (obj) => {
                let ret = "";
                ret += `<div class="header_div" style="user-select: auto;"><img class="header_image" src="static/img/header.png" alt="..."></div>`
                ret += `<h3 class='threebot_name'><b>3bot name:</b> ${obj.threebot_name}</h3>
                        <p class='threebot_id'><b>3bot id:</b> ${obj.threebot_id}</p>`;
                ret += `<p class="jsx_version"><b>JSX Version: </b>${obj.jsx_version}</p>`
                for (let i in obj.interfaces) {
                    let intfc = obj.interfaces[i];
                    ret += `<b>${intfc.name}:</b><br>
                            <b>IP:</b> ${intfc.ip}<br>
                            <b>IPv6:</b> ${intfc.ip6}<br>`
                }
                return ret;
            }
        }
    }

    init() {
        const jsx_info = {
            'threebot_name': 'Mohamed',
            'threebot_id': '123',
            'jsx_version': '2.5.6',
            'interfaces': [{
                'name': 'eth0',
                'ip': '120.5.6.1',
                'ip6': '1.2.4.5.6.5.4'
            }]
        }
        $$("jsx_info").parse(jsx_info);

        // call service
        
        // admin.hello().then((data)=>{
        //     console.log("resulte: ",data.json())
        // }).catch((error)=>{
        //     console.log(error)
        // })

    }
}
