import math
from jumpscale.sals.marketplace import deployer

from jumpscale.packages.marketplace.chats.publisher import Publisher
from jumpscale.sals.chatflows.chatflows import chatflow_step


class WebsiteDeploy(Publisher):

    title = "Deploy Website"
    SOLUTION_TYPE = "website"  # chatflow used to deploy the solution

    @chatflow_step(title="Website Set Up")
    def configuration(self):
        form = self.new_form()
        title = form.string_ask("Title", required=True)
        url = form.string_ask("Repository URL", required=True)
        branch = form.string_ask("Branch", required=True)
        form.ask("Set Configuration")
        self.user_email = self.user_info()["E-mail"]
        self.envars = {
            "TYPE": "www",
            "NAME": "entrypoint",
            "TITLE": title.value,
            "URL": url.value,
            "BRANCH": branch.value,
            "EMAIL": self.user_email,
        }


chat = WebsiteDeploy
