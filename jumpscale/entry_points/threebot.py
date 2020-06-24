import sys

import click

from jumpscale.loader import j
from jumpscale.threesdk.identitymanager import IdentityManager

SERVICES_PORTS = {"nginx": 8999, "nginx_http": 80, "nginx_https": 443, "gedis": 16000}


@click.command()
@click.option("--identity", default=None, help="threebot name(i,e name.3bot)")
def start(identity=None):
    """start 3bot server after making sure identity is ok
    It will start with the default identity in j.me, if you'd like to specify an identity
    please pass the optional arguments

    usage: threebot start
    or: threebot start --identity <identity> --explorer <explorer>

    Args:
        identity (str, optional): threebot name. Defaults to None.
        explorer (str, optional): which explorer network to use: mainnet, testnet, devnet. Defaults to None.
    """
    if identity:
        if j.core.identity.find(identity):
            print(f"Setting default identity to {identity}\nStarting threebot server...")
            j.core.identity.set_default(identity)
            j.core.identity.me.save()
        else:
            j.tools.console.printcolors(
                "{RED}Identity %s is not set, please configure it or start with the default one" % identity
            )
            sys.exit(1)

    if not j.core.identity.list_all():
        identity_data = IdentityManager()
        identity_info = identity_data.ask_identity()
        me = j.core.identity.new(
            "default",
            tname=identity_info.identity,
            email=identity_info.email,
            words=identity_info.words,
            explorer_url=f"https://{identity_info.explorer}/explorer",
        )
        me.register()
        me.save()

    used_ports = []
    ports_error_msg = ""
    for service_name, service_port in SERVICES_PORTS.items():
        if j.sals.process.is_port_listenting(service_port):
            used_ports.append((service_name, service_port))
            ports_error_msg += f" {service_name}:{service_port}"

    msg = (
        f"{{RED}}Threebot server is running already or ports{{CYAN}}{ports_error_msg}{{RED}}\n"
        "are being held by your system\n"
        f"Please use {{WHITE}}threebot stop{{RED}} to stop your threebot server or free the ports to be able to start the threebot server"
    )

    if used_ports:
        j.tools.console.printcolors(msg)
        sys.exit(1)

    cmd = j.tools.startupcmd.get("threebot_default")
    cmd.start_cmd = "jsng 'j.servers.threebot.start_default(wait=True)'"
    cmd.process_strings_regex = [j.tools.nginx.get("default").check_command_string, "nginx.*"]
    cmd.ports = [8000, 8999]
    cmd.start()
    print("\n✅ Threebot server started\n")
    if j.sals.process.in_host():
        j.tools.console.printcolors("{WHITE}Visit admin dashboard at: {GREEN}http://localhost/\n")


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
