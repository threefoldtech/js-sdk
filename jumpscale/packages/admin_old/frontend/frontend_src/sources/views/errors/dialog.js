import { JetView } from "webix-jet";

import { ansiUp } from "../../common/colors";

export class ErrorView extends JetView {
    config() {
        const message = {
            view: "template",
            id: "error_template",
            template: "",
            scroll: "xy"
        };

        return {
            view: "window",
            head: "Error",
            modal: true,
            width: window.innerWidth * .8,
            height: window.innerHeight * .8,
            position: "center",
            body: {
                rows: [
                    message,
                    {
                        view: "button",
                        value: "OK",
                        css: "webix_primary",
                        click: function () {
                            this.getTopParentView().hide();
                        }
                    }
                ]
            }
        }
    }

    init() {
        this.message = $$("error_template");
    }

    showError(message, head) {
        this.message.setHTML(`<p>${ansiUp.ansi_to_html(message)}</p>`);
        if (head) {
            this.message.getHead().setHTML(head);
        }

        this.getRoot().show();
    }
}
