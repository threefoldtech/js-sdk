import { JetView } from "webix-jet";
import { packages } from "../../services/packages"

export class ExternalView extends JetView {
    constructor(app, name, targetUrl, requiredPackages) {
        super(app, name);

        this.targetUrl = targetUrl || "/";
        this.requiredPackages = requiredPackages || {}; // required packages as (name: git_url) pairs
    }

    config() {
        const self = this;
        const iframe = {
            view: "iframe",
            localId: "iframe-external",
            on: {
                onAfterLoad: function () {
                    if (this.hideProgress) {
                        this.hideProgress();
                    }
                    this.enable();
                }
            }
        };

        return {
            rows: [{
                localId: "install-packages",
                hidden: true,
                cols: [
                    {
                        localId: "required_packages_div",
                        view: "template",
                        autoheight: true,
                    }, {
                        view: "button",
                        localId: "install_btn",
                        value: "Install required packages",
                        css: "webix_primary",
                        height: 50,
                        click: self.installRequiredPackages.bind(self)
                    }, {
                        view: "button",
                        localId: "go_to_packages_btn",
                        value: "Go to packages and install them manually",
                        css: "webix_primary",
                        height: 50,
                        click: function () {
                            this.$scope.show("/main/packages");
                        }
                    }
                ]
            }, iframe]
        }
    }

    installRequiredPackages() {
        let promises = Object.values(this.packagesToInstall).map((path) => {
            console.log(path)
            return packages.add(null, path); // add by git url
        });

        this.installButton.disable();

        Promise.all(promises).then(() => {
            webix.message({ type: "success", text: "All required packages installed successfully, page will be reloaded in 2 seconds" });
            setInterval(() => window.location.reload(true), 2000);
        }).catch(() => {
            webix.message({ type: "error", text: "An error occurred, please try installing from packages for more details" });
        });
    }

    showIframe() {
        this.externalIframe.show();
        this.externalIframe.showProgress({ type: "icon" });
        this.externalIframe.load(this.targetUrl);
    }

    init(view) {
        const self = this;
        this.externalIframe = this.$$("iframe-external");
        this.externalIframe.disable();
        self.packagesToInstall = {};

        webix.extend(this.externalIframe, webix.ProgressBar);

        self.requiredPackagesNames = Object.keys(self.requiredPackages); // only names

        if (!self.requiredPackagesNames.length) {
            self.showIframe();
            return;
        }

        self.requiredPackagesDiv = self.$$("required_packages_div");
        self.installPackageContainer = self.$$("install-packages");
        self.installButton = self.$$("install_btn");

        // check which packages to install
        // if any is already installed, then just ignore it
        packages.getInstalledPackages().then(data => {
            const packageList = JSON.parse(data.json()).data;

            // now go over required packages
            for (let name of self.requiredPackagesNames) {
                // check if a required package is already installed
                if (packageList.includes(name)) {
                    continue;
                }

                self.packagesToInstall[name] = self.requiredPackages[name];
            }

            // check packages to be installed again if still need to install any of them
            const packageNamesToInstall = Object.keys(self.packagesToInstall);
            if (packageNamesToInstall.length) {
                self.installPackageContainer.show();
                self.externalIframe.hide();

                const names = packageNamesToInstall.join(", ");
                self.requiredPackagesDiv.setHTML(
                    `<div style='width:auto;text-align:center'><h3>You need to install the following required packages: ${names}<h3/></div>`
                );
            } else {
                self.installPackageContainer.hide();
                self.showIframe()
            }
        });
    }
}
