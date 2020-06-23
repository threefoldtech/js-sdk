import binascii
import os

import click
import requests
from nacl.signing import SigningKey

from jumpscale.loader import j
from jumpscale.tools.console import ask_choice, ask_string

from . import english, helper

NETWORKS = {"mainnet": "explorer.grid.tf", "testnet": "explorer.testnet.grid.tf", "devnet": "explorer.devnet.grid.tf"}


class IdentityManager:
    def __init__(self, identity: str = "", email: str = None, words: str = None, explorer: str = None):
        self.identity = identity
        self.email = email
        self.words = words
        self.explorer = explorer

    def reset(self):
        self.identity = ""
        self.email = ""
        self.words = ""
        self.explorer = ""

    def _check_keys(self, user_explorer_key, user_app):
        if not user_app:
            return True
        pub_key_app = j.data.serializers.base64.decode(user_app["publicKey"])
        if binascii.unhexlify(user_explorer_key) != pub_key_app:
            return False
        return True

    def _get_user(self):
        response = requests.get(f"https://login.threefold.me/api/users/{self.identity}")
        if response.status_code == 404:
            raise j.core.exceptions.Value(
                "\nThis identity does not exist in 3bot mobile app connect, Please create an idenity first using 3Bot Connect mobile Application\n"
            )
        userdata = response.json()

        resp = requests.get("https://{}/explorer/users".format(self.explorer), params={"name": self.identity})
        if resp.status_code == 404 or resp.json() == []:
            return None, userdata
        else:
            users = resp.json()

            if not self._check_keys(users[0]["pubkey"], userdata):
                raise j.core.exceptions.Value(
                    f"\nYour 3bot on {self.explorer} seems to have been previously registered with a different public key.\n"
                    "Please contact support.grid.tf to reset it.\n"
                    "Note: use the same email registered on the explorer to contact support otherwise we cannot reset the account.\n"
                )

            if users:
                return (users[0], userdata)
            return None, userdata

    def _check_email(self, email):
        resp = requests.get("https://{}/explorer/users".format(self.explorer), params={"email": email})
        users = resp.json()
        if users:
            return True
        return False

    def ask_identity(self, identity=None, explorer=None):
        def _fill_identity_args(identity, explorer):
            def fill_words():
                words = ask_string("Copy the phrase from your 3bot Connect app here.")
                self.words = words

            def fill_identity():
                identity = ask_string("what is your threebot name (identity)?")
                if "." not in identity:
                    identity += ".3bot"
                self.identity = identity

            if identity:
                if self.identity != identity and self.identity:
                    self.reset()
                self.identity = identity

            if explorer:
                self.explorer = explorer
            elif not self.explorer:
                response = ask_choice(
                    "Which network would you like to register to? ", ["mainnet", "testnet", "devnet", "none"]
                )
                self.explorer = NETWORKS.get(response, None)
            if not self.explorer:
                return True

            user = None
            while not user:
                fill_identity()
                try:
                    user, user_app = self._get_user()
                except j.core.exceptions.Value as e:
                    response = ask_choice(f"{e}. What would you like to do?", ["restart", "reenter"],)
                    if response == "restart":
                        return False

            while not self.email:
                self.email = ask_string("What is the email address associated with your identity?")
                if self._check_email(self.email):
                    break
                else:
                    self.email = None
                    response = ask_choice(
                        "This email is currently associated with another identity. What would you like to do?",
                        ["restart", "reenter"],
                    )
                    if response == "restart":
                        return False

            print("Configured email for this identity is {}".format(self.email))

            if not self.words:
                fill_words()

            # time to do validation of words
            while True:
                try:
                    seed = helper.to_entropy(self.words, english.words)
                    key = SigningKey(seed)
                    hexkey = binascii.hexlify(key.verify_key.encode()).decode()
                    if (user and hexkey != user["pubkey"]) or not self._check_keys(hexkey, user_app):
                        raise Exception
                    else:
                        return True
                except Exception:
                    choice = ask_choice(
                        "\nSeems one or more more words entered is invalid.\n" " What would you like to do?\n",
                        ["restart", "reenter"],
                    )
                    if choice == "restart":
                        return False
                    fill_words()
                    continue

        while True:
            if _fill_identity_args(identity, explorer):
                return self.identity, self.email, self.words, self.explorer


@click.command()
@click.option("--identity", default=None, help="threebot name(i,e name.3bot)")
@click.option("--email", default=None, help="threebot email registerd with in 3bot app")
@click.option("--words", default=None, help="seed phrase of the user from 3bot app")
@click.option("--explorer", default=None, help="which explorer network to use: mainnet, testnet, devnet")
def start(identity=None, email=None, words=None, explorer=None):
    """start 3bot server after making sure identity is ok
    It will start with the default identity in j.me, if you'd like to specify an identity
    please pass the optional arguments

    usage: threebot start
    or: threebot start --identity <identity> --email <email> --words <words> --explorer <explorer>

    Args:
        identity (str, optional): threebot name. Defaults to None.
        email (str, optional): threebot email. Defaults to None.
        words (str, optional): seed phrase of the user. Defaults to None.
        explorer (str, optional): which explorer network to use: mainnet, testnet, devnet. Defaults to None.
    """
    if identity or email or words or explorer or not j.core.identity.list_all():
        identity_data = IdentityManager(identity=identity, email=email, words=words, explorer=explorer)
        identity, email, words, explorer = identity_data.ask_identity(identity, explorer)
        me = j.core.identity.new(
            "default", tname=identity, email=email, words=words, explorer_url=f"https://{explorer}/explorer"
        )
        me.register()
        me.save()
        j.core.identity.set_default("default")

    cmd = j.tools.startupcmd.get("threebot_default")
    cmd.start_cmd = "jsng 'j.servers.threebot.start_default(wait=True)'"
    cmd.process_strings_regex = [j.tools.nginx.get("default").check_command_string, "nginx.*"]
    cmd.ports = [8000, 8999]
    cmd.start()
    print("\n✅ Threebot server started")


@click.command()
def stop():
    """stops threebot server
    """
    cmd = j.tools.startupcmd.get("threebot_default")
    cmd.stop()
    print("Threebot server Stopped")


@click.group()
def cli():
    pass


cli.add_command(start)
cli.add_command(stop)


if __name__ == "__main__":
    cli()
