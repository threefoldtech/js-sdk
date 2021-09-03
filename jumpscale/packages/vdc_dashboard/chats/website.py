from jumpscale.packages.vdc_dashboard.chats.publisher import Publisher
from jumpscale.sals.chatflows.chatflows import chatflow_step


class WebsiteDeploy(Publisher):
    SOLUTION_TYPE = "website"
    EXAMPLE_URL = "https://github.com/threefoldfoundation/website_example"
    DOC_URL = "https://wiki.cloud.threefold.io/#/evdc_website"

    title = "Website"

    def get_config(self):
        return {
            "env.type": "www",
            "env.url": self.config.chart_config.url,
            "env.branch": self.config.chart_config.branch,
            "env.srcdir": self.config.chart_config.srcdir,
            "ingress.host": self.config.chart_config.domain,
            "nameOverride": self.SOLUTION_TYPE,
        }

    @chatflow_step(title="Configurations")
    def set_config(self):
        form = self.new_form()
        url = form.string_ask("Repository URL", required=True, is_git_url=True)
        branch = form.string_ask("Branch", required=True)
        srcdir = form.string_ask("Source directory", required=False, default="html")
        msg = self.get_mdconfig_msg()
        form.ask(msg, md=True)

        self.config.chart_config.url = url.value
        self.config.chart_config.branch = branch.value
        self.config.chart_config.srcdir = srcdir.value


chat = WebsiteDeploy
