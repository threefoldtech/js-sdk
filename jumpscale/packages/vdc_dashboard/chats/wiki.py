from jumpscale.packages.vdc_dashboard.chats.publisher import Publisher
from jumpscale.sals.chatflows.chatflows import chatflow_step


class WikiDeploy(Publisher):
    SOLUTION_TYPE = "wiki"
    EXAMPLE_URL = "https://github.com/threefoldfoundation/wiki_example"

    title = "Wiki"

    @chatflow_step(title="Configurations")
    def set_config(self):
        self._choose_flavor()

        form = self.new_form()
        url = form.string_ask("Repository URL", required=True, is_git_url=True)
        branch = form.string_ask("Branch", required=True)
        srcdir = form.string_ask("Source directory", required=False, default="src")
        msg = self.get_mdconfig_msg()
        form.ask(msg, md=True)
        self.chart_config.update(
            {
                "env.type": "wiki",
                "env.url": url.value,
                "env.branch": branch.value,
                "env.srcdir": srcdir.value,
                "ingress.host": self.domain,
                "resources.limits.cpu": self.resources_limits["cpu"],
                "resources.limits.memory": self.resources_limits["memory"],
                "nameOverride": self.SOLUTION_TYPE,
            }
        )


chat = WikiDeploy
