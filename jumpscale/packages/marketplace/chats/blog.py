from jumpscale.packages.marketplace.chats.publisher import Publisher
from jumpscale.sals.chatflows.chatflows import chatflow_step


class BlogDeploy(Publisher):

    title = "Deploy a Blog"
    SOLUTION_TYPE = "blog"  # chatflow used to deploy the solution

    @chatflow_step(title="blog Setup")
    def configuration(self):
        form = self.new_form()
        title = form.string_ask("Title", required=True)
        url = form.string_ask("Repository URL", required=True)
        branch = form.string_ask("Branch", required=True)
        form.ask("Set Configuration")
        self.user_email = self.user_info()["email"]
        self.envars = {
            "TYPE": "blog",
            "NAME": "entrypoint",
            "TITLE": title.value,
            "URL": url.value,
            "BRANCH": branch.value,
            "EMAIL": self.user_email,
        }


chat = BlogDeploy
