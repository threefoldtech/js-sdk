import "./styles/app.css";
import {JetApp, plugins} from "webix-jet";

export default class InventoryApp extends JetApp {
	constructor(config){
		super(webix.extend({
			id:			APPNAME,
			version:	VERSION,
			start:		"/main/dash",
			debug:		!PRODUCTION
		}, config, true));

		/* error tracking */
		this.attachEvent("app:error:resolve", function(name, error){
			window.console.error(error);
		});

		let localeConfig = {
			webix:{
				en:"en-US",
				zh:"zh-CN",
				es:"es-ES",
				ko:"ko-KR",
				ru:"ru-RU",
				de:"de-DE"
			}
		};
		this.use(plugins.Locale,localeConfig);
	}
}
