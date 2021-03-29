from textwrap import dedent

from jumpscale.packages.vdc_dashboard.chats.publisher import Publisher
from jumpscale.sals.chatflows.chatflows import chatflow_step


class BlogDeploy(Publisher):
    SOLUTION_TYPE = "blog"
    EXAMPLE_URL = "https://github.com/threefoldfoundation/blog_example"
    DOC_URL = "https://wiki.cloud.threefold.io/#/evdc_blog"
    title = "Blog"

    def get_config(self):
        return {
            "env.type": "blog",
            "env.url": self.config.chart_config.url,
            "env.branch": self.config.chart_config.branch,
            "ingress.host": self.config.chart_config.domain,
            "nameOverride": self.SOLUTION_TYPE,
        }

    def get_mdconfig_msg(self):
        # blog does not need a source directory
        msg = dedent(
            f"""\
        Few parameters are needed to be able to publish your content online
        - Create a github account
        - Fork the following [template repository]({self.EXAMPLE_URL}) and add your content there.
        - Copy your forked repository URL to this deployer
        - Select the branch you want to deploy, e.g: main

        For more information about repository structure and examples please check [the manual]({self.DOC_URL})
        """
        )
        return msg

    @chatflow_step(title="Configurations")
    def set_config(self):
        form = self.new_form()
        url = form.string_ask("Repository URL", required=True, is_git_url=True)
        branch = form.string_ask("Branch", required=True)
        msg = self.get_mdconfig_msg()
        form.ask(msg, md=True)

        self.config.chart_config.url = url.value
        self.config.chart_config.branch = branch.value


chat = BlogDeploy
