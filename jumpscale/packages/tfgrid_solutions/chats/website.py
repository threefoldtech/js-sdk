import math
from jumpscale.sals.reservation_chatflow import deployer

from jumpscale.packages.tfgrid_solutions.chats.publisher import Publisher
from jumpscale.sals.chatflows.chatflows import chatflow_step


class WebsiteDeploy(Publisher):

    title = "Deploy a Website"
    publishing_chatflow = "Website"  # chatflow used to deploy the solution

    @chatflow_step(title="Website Set Up")
    def configuration(self):
        form = self.new_form()
        title = form.string_ask("Title", required=True)
        url = form.string_ask("Repository url", required=True)
        branch = form.string_ask("Branch", required=True)
        form.ask("Set configuration")
        self.user_email = self.user_info()["email"]
        self.envars = {
            "TYPE": "www",
            "NAME": "entrypoint",
            "TITLE": title.value,
            "URL": url.value,
            "BRANCH": branch.value,
            "EMAIL": self.user_email,
        }

        query = {
            "cru": self.resources["cpu"],
            "mru": math.ceil(self.resources["memory"] / 1024),
            "sru": math.ceil(self.resources["disk_size"] / 1024),
        }
        self.selected_node = deployer.schedule_container(self.pool_id, **query)


chat = WebsiteDeploy
