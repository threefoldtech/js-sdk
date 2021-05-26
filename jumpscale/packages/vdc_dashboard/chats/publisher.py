from textwrap import dedent

from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy


class Publisher(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "publishingtools"
    HELM_REPO_NAME = "marketplace"
    CHART_NAME = "publishingtools"

    EXAMPLE_URL = "https://github.com/threefoldfoundation/info_gridmanual"
    DOC_URL = "https://now.threefold.io/now/docs/publishing-tool/#repository-examples"

    title = "Publisher"
    steps = [
        "init_chatflow",
        "get_release_name",
        "choose_flavor",
        "set_config",
        "create_subdomain",
        "install_chart",
        "initializing",
        "success",
    ]

    def get_config(self):
        return {
            "env.type": self.config.chart_config.site_type,
            "env.url": self.config.chart_config.url,
            "env.branch": self.config.chart_config.branch,
            "env.srcdir": self.config.chart_config.srcdir,
            "ingress.host": self.config.chart_config.domain,
        }

    def get_mdconfig_msg(self):
        msg = dedent(
            f"""\
        Few parameters are needed to be able to publish your content online
        - Create a github account
        - Fork the following [template repository]({self.EXAMPLE_URL}) and add your content there.
        - Copy your forked repository URL to this deployer
        - Select the branch you want to deploy, e.g: main
        - Identify which source directory where the content lives in, e.g. src, html...

        For more information about repository structure and examples please check [the manual]({self.DOC_URL}).
        """
        )
        return msg

    @chatflow_step(title="Configurations")
    def set_config(self):
        form = self.new_form()
        site_type = form.single_choice(
            "Choose the publication type", options=["wiki", "www", "blog"], default="wiki", required=True
        )
        url = form.string_ask("Repository URL", required=True, is_git_url=True)
        branch = form.string_ask("Branch", required=True)
        srcdir = form.string_ask("Source directory", required=False, default="")
        msg = self.get_mdconfig_msg()
        form.ask(msg, md=True)

        self.config.chart_config.site_type = site_type.value
        self.config.chart_config.url = url.value
        self.config.chart_config.branch = branch.value
        self.config.chart_config.srcdir = srcdir.value


chat = Publisher
