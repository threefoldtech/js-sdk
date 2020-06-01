import { JetView, plugins } from "webix-jet";

export default class TopView extends JetView {
    config() {
        const _ = this.app.getService("locale")._;

        const header = {
            cols: [
                {
                    id: "button_hide_menu",
                    view: "icon", icon: "mdi mdi-menu",
                    css: "custom_dark",
                    height: 58,
                    click: this.hideMenu,
                    tooltip: "Hide menu",
                },
                {
                    id: "header",
                    type: "header",
                    css: "custom_dark",
                    height: 58,
                    template: "ADMIN",
                    borderless: true,
                },
            ]
        };

        const sidebarData = [{
            id: "dash",
            value: "Dashboard",
            icon: "mdi mdi-view-dashboard"
        },
        {
            id: "wikis",
            value: "Packages Docs",
            icon: "mdi mdi-newspaper"
        },
        {
            id: "alerts",
            value: "Alerts",
            icon: "mdi mdi-bell-alert"
        },
        {
            id: "logs",
            value: "Logs",
            icon: "mdi mdi-history"
        },
        {
            id: "tfwikis_main",
            value: "TF Wikis",
            icon: "mdi mdi-animation-play",
            data: [{
                id: "tfgridsdk",
                icon: "mdi mdi-book-open",
                value: "TFGridSDK"
            }, {
                id: "threefold",
                icon: "mdi mdi-worker",
                value: "Threefold"
            }]
        },
        {
            id: "packages",
            value: "Packages",
            icon: "mdi mdi-package"
        },
        {
            id: "deployedSolutions",
            value: "Solutions",
            icon: "mdi mdi-animation-play",
            data: [{
                id: "deployed_network",
                value: '<span><img class="solutions-icon" src="static/img/network.png"/>Network</span>'
            }, {
                id: "deployed_ubuntu",
                value: '<span><img class="solutions-icon" src="static/img/ubuntu.png"/>Ubuntu</span>'
            }, {
                id: "deployed_flist",
                value: '<span><img class="solutions-icon" src="static/img/flist.png"/>Generic flist</span>'
            }, {
                id: "deployed_minio",
                value: '<span><img class="solutions-icon" src="static/img/minio.png"/>Minio / S3</span>'
            }, {
                id: "deployed_k8s_cluster",
                value: '<span><img class="solutions-icon" src="static/img/k8s.png"/>Kubernetes Cluster</span>'
            }, {
                id: "deployed_gitea",
                value: '<span><img class="solutions-icon" src="static/img/gitea.png"/>Gitea</span>'
            }, {
                id: "deployed_domain_delegation",
                value: '<span><img class="solutions-icon" src="static/img/domain.png"/>Domain Delegation</span>'
            }, {
                id: "deployed_solution_expose",
                value: '<span><img class="solutions-icon" src="static/img/wan.png"/>Solution Expose</span>'
            }, {
                id: "deployed_gateway_4to6",
                value: '<span><img class="solutions-icon" src="static/img/ip.png"/>4 to 6 Gateway</span>'
            }
            ]
        },
        {
            id: "walletsManager",
            value: "Wallets Manager",
            icon: "mdi mdi-wallet"
        },
        {
            id: "capacity",
            value: "Capacity",
            icon: "mdi mdi-server"
        },
        {
            id: "farmmanagement",
            value: "Farm Management",
            icon: "mdi mdi-server"
        },
        {
            id: "sdkexamples",
            value: "SDK Examples",
            icon: "mdi mdi-file"
        },
        {
            id: "codeserver",
            value: "Codeserver",
            icon: "mdi mdi-code-tags"
        },
        {
            id: "jupyter",
            value: "TF Simulator",
            icon: "mdi mdi-play"
        },
        {
            id: "settings",
            value: "Settings",
            icon: "mdi mdi-settings"
        },
        ]


        const sidebar = {
            localId: "menu",
            view: "sidebar",
            css: "webix_dark admin_sidebar",
            width: 230,
            data: sidebarData,
            scroll: "y",
            on: {
                // this is for refreshing view on selecting current selected item
                onItemClick: function (id) {
                    this.unselect(id);
                    this.select(id);
                }
            }
        };

        const toolbar = {
            view: "toolbar",
            padding: 9,
            height: 58,
            cols: [{
                id: "button_show_menu",
                view: "icon",
                icon: "mdi mdi-menu",
                click: this.showMenu,
                hidden: true, // hidden by default
                tooltip: "Show menu",
            },
            {
                view: "template",
                template: `<img class="webix_icon" src="static/img/3bot.png"/>`,
                borderless: true,
                height: 40,
            },
            { batch:"default" },
            {
                view: "icon",
                icon: "mdi mdi-bell",
                badge: 0,
                batch: "default",
                localId: "bell",
                tooltip: _("View the latest notifications"),
                // click: function () {
                //     this.$scope.notifications.showWindow(this.$view);
                // }
            },
            {
                id: "username_label",
                view: "label",
                label: "username",
                borderless: true,
            },
            {
                id: "user_icon",
                view: "icon",
                icon: "mdi mdi-account-circle",
                borderless: true,
                popup: "user_menu"
            }
            ]
        };

        return {
            type: "clean",
            cols: [{
                rows: [header, sidebar]
            },
            {
                rows: [
                    toolbar,
                    {
                        $subview: true
                    }
                ]
            }
            ]
        };
    }

    showMenu() {
        this.$scope.menu.show();
        this.$scope.header.show();
        this.$scope.buttonHideMenu.show();

        this.$scope.buttonShowMenu.hide();
    }

    hideMenu() {
        this.$scope.menu.hide();
        this.$scope.header.hide();
        this.$scope.buttonHideMenu.hide();

        this.$scope.buttonShowMenu.show();
    }

    init() {
        var self = this;

        this.use(plugins.Menu, {
            id: "menu",
            urls: {
                tfgridsdk: "tfwikis.tfgridsdk",
                threefold: "tfwikis.threefold",
            }
        });

        this.menu = this.$$("menu");
        this.header = this.$$("header");
        this.notificationsBell = this.$$("bell");

        this.buttonShowMenu = this.$$("button_show_menu");
        this.buttonHideMenu = this.$$("button_hide_menu");

        this.on(this.app,"read:notifications",() => {
			this.notificationsBell.config.badge = 0;
			this.notificationsBell.refresh();
        });

        this.on(this.app, "update:badge", (data) => {
			this.notificationsBell.config.badge += data;
			this.notificationsBell.refresh();
		});

        this.webix.ui({
            view: "submenu",
            id: "user_menu",
            autowidth: true,
            data: []
        });
    }
}
