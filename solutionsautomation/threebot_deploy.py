from gedispatch import GedisChatBotPatch
from jumpscale.packages.threebot_deployer.chats.threebot import ThreebotDeploy
from time import time


class ThreebotDeployAutomated(GedisChatBotPatch, ThreebotDeploy):
    MESSAGE_NAME = "Just like humans, each 3Bot needs their own unique identity to exist on top of the Threefold Grid. Please enter a name for your new 3Bot. This name will be used as the web address that could give you access to your 3Bot anytime."
    SECRET = "Please enter the recovery secret (using this recovery secret, you can recover any 3Bot you deploy online)"
    EXPIRATION = "Please enter the expiration date of your 3Bot. This will be used to calculate the amount of capacity you need to keep your 3Bot alive and build projects on top of the TF Grid. But no worries, you could always extend your 3Bot’s lifetime on 3Bot Deployer's home screen"
    CURRENCY = "Please select the currency you would like to pay your 3Bot deployment with."
    QS = {
        MESSAGE_NAME: "get_name",
        SECRET: "secret",
        EXPIRATION: "expiration",
        CURRENCY: "currency",
    }


ThreebotDeployAutomated(
    solution_name="test_threebot", secret="hassan", expiration=time() * 60 + 15, currency="FreeTFT", debug=True,
)
