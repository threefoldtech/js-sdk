import os

import click

from jumpscale.loader import j
from jumpscale.threesdk.threebot import ensure_identity

NETWORKS = {"mainnet": "explorer.grid.tf", "testnet": "explorer.testnet.grid.tf", "devnet": "explorer.devnet.grid.tf"}


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
        identity_data = ensure_identity(identity=identity, email=email, words=words, explorer=explorer)
        if not identity_data:
            raise j.core.exceptions.Input("Please provide correct identity information")

        identity, email, words, explorer = identity_data
        me = j.core.identity.new(
            "default", tname=identity, email=email, words=words, explorer_url=f"https://{NETWORKS[explorer]}/explorer"
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
