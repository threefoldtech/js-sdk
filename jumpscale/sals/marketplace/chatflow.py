from jumpscale.core.base import StoredFactory
from jumpscale.loader import j
from jumpscale.packages.marketplace.bottle.models import UserEntry
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow


class MarketPlaceChatflow(GedisChatBot):
    def _validate_user(self):
        tname = self.user_info()["username"].lower()
        user_factory = StoredFactory(UserEntry)
        explorer_url = j.core.identity.me.explorer.url

        if "testnet" in explorer_url:
            explorer_name = "testnet"
        elif "devnet" in explorer_url:
            explorer_name = "devnet"
        elif "explorer.grid.tf" in explorer_url:
            explorer_name = "mainnet"
        else:
            raise StopChatFlow(f"Unsupported explorer {explorer_url}")
        instance_name = f"{explorer_name}_{tname.replace('.3bot', '')}"
        if instance_name in user_factory.list_all():
            user_entry = user_factory.get(instance_name)
            if not user_entry.has_agreed:
                raise StopChatFlow(
                    f"You must accept terms and conditions before using this solution. please head towards the main page to read our terms"
                )
        else:
            raise StopChatFlow(
                f"You must accept terms and conditions before using this solution. please head towards the main page to read our terms"
            )
