from jumpscale.packages.marketplace.chats.publisher import Publisher
from jumpscale.sals.chatflows.chatflows import chatflow_step


class WikiDeploy(Publisher):

    title = "Deploy Wiki"
    welcome_message = "This wizard will help you publish your wiki."
    publishing_chatflow = "wiki"  # chatflow used to deploy the solution

    @chatflow_step(title="Wiki Setup")
    def configuration(self):
        form = self.new_form()
        title = form.string_ask("Title", required=True)
        url = form.string_ask("Repository url", required=True)
        branch = form.string_ask("Branch", required=True)
        form.ask("Set configuration")

        self.envars = {
            "TYPE": "wiki",
            "NAME": "entrypoint",
            "TITLE": title.value,
            "URL": url.value,
            "BRANCH": branch.value,
            "EMAIL": self.user_info()["email"],
        }


chat = WikiDeploy
