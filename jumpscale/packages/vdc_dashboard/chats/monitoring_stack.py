from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step
from jumpscale.sals.vdc import VDCFACTORY


class InstallMonitoringStack(GedisChatBot):
    title = "Monitoring Stack"
    steps = ["confirm", "success"]

    @chatflow_step(title="Confirmation")
    def confirm(self):
        vdc_full_name = list(j.sals.vdc.list_all())[0]
        self.vdc = VDCFACTORY.find(vdc_full_name, load_info=True)
        vdc_deployer = self.vdc.get_deployer()
        self.public_ip = self.single_choice(
            "Do you want to Deploy the monitoring stack which contains (Grafana, Prometheus, Redis) on your VDC?",
            options=["Yes", "No"],
            default="Yes",
            required=True,
        )
        if self.public_ip == "No":
            self.stop("The selected option was No, Please go back to the marketplace to install other solutions.")
        else:
            try:
                vdc_deployer.monitoring.deploy_stack()
            except j.exceptions.Runtime as e:
                self.stop(message=f"failed to deploy monitoring stack due to error {str(e)}")

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        self.md_show(f"""You have deployed the monitoring stack on VDC: {self.vdc.vdc_name} successfuly""")


chat = InstallMonitoringStack
