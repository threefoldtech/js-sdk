import { JetView, plugins } from "webix-jet";
import { auth } from "../services/auth";

export default class TopView extends JetView {
    config() {
        const header = {
            cols: [{
                id: "button_hide_menu",
                view: "icon",
                icon: "mdi mdi-menu",
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
                id: "deployed_monitoring",
                value: '<span><img class="solutions-icon" src="static/img/monitoring.png"/>Monitoring</span>'
            }, {
                id: "deployed_domain_delegation",
                value: '<span><img class="solutions-icon" src="static/img/domain.png"/>Domain Delegation</span>'
            }, {
                id: "deployed_solution_expose",
                value: '<span><img class="solutions-icon" src="static/img/wan.png"/>Solution Expose</span>'
            }, {
                id: "deployed_gateway_4to6",
                value: '<span><img class="solutions-icon" src="static/img/ip.png"/>4 to 6 Gateway</span>'
            }, {
                id: "all_reservations",
                value: '<span><img class="solutions-icon" src="static/img/3bot.ico"/>All reservations</span>'
            }]
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
            id: "codeserver",
            value: "Codeserver",
            icon: "mdi mdi-code-tags"
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
                all_reservations: "solutions.allReservations",
                deployed_network: "solutions.network",
                deployed_ubuntu: "solutions.ubuntu",
                deployed_flist: "solutions.flist",
                deployed_minio: "solutions.minio",
                deployed_k8s_cluster: "solutions.k8sCluster",
                deployed_gitea: "solutions.gitea",
                deployed_domain_delegation: "solutions.domainDelegation",
                deployed_solution_expose: "solutions.solutionExpose",
                deployed_gateway_4to6: "solutions.4to6Gateway",
                deployed_monitoring: "solutions.monitoring",
            }
        });

        this.menu = this.$$("menu");
        this.header = this.$$("header");

        this.buttonShowMenu = this.$$("button_show_menu");
        this.buttonHideMenu = this.$$("button_hide_menu");

        this.webix.ui({
            view: "submenu",
            id: "user_menu",
            autowidth: true,
            data: []
        });

        this.userMenu = $$("user_menu");
        this.userMenu.attachEvent("onItemClick", function (id, e, node) {
            if (id == "logout") {
                window.location.href = "/auth/login";
            }
        });

        this.usernameLabel = $$("username_label");

        auth.getAuthenticatedUser().then(data => {
            const userInfo = data.json();
            let username = userInfo.username;

            self.usernameLabel.config.label = username;
            self.usernameLabel.config.width = webix.html.getTextSize(username).width + 10;
            self.usernameLabel.resize();

            self.userMenu.add({ id: 'email', value: userInfo.email })
            self.userMenu.add({ id: 'logout', value: "Logout" })
        }).catch(() => {
            this.webix.message("Error on getting current user")
        });

        // to check on first init view
        let width = document.documentElement.clientWidth;
        let height = document.documentElement.clientHeight;
        let menuOpen = true;

        if (width < 1600 && menuOpen) {
            self.menu.hide();
            self.header.hide();
            self.buttonHideMenu.hide();
            self.buttonShowMenu.show();
            menuOpen = false
        } else if (width > 1600 && !menuOpen) {
            self.menu.show();
            self.header.show();
            self.buttonHideMenu.show();
            self.buttonShowMenu.hide();
            menuOpen = true;
        }

        window.onresize = function (event) {
            var width = document.documentElement.clientWidth;
            var height = document.documentElement.clientHeight;

            if (width < 1600 && menuOpen) {
                self.menu.hide();
                self.header.hide();
                self.buttonHideMenu.hide();
                self.buttonShowMenu.show();
                menuOpen = false
            } else if (width > 1600 && !menuOpen) {
                self.menu.show();
                self.header.show();
                self.buttonHideMenu.show();
                self.buttonShowMenu.hide();
                menuOpen = true;
            }
        };
    }
}
