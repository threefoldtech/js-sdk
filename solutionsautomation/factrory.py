from gitea import GiteaAutomated
from cryptpad import CryptpadAutomated
from wiki import WikiAutomated
from website import WebsiteAutomated
from blog import BlogAutomated
from ubuntu import UbuntuAutomated
from mattermost import MattermostAutomated
from discourse import DiscourseAutomated
from peertube import PeertubeAutomated


def deploy_gitea(solution_name, currency, expiration, wg_config="NO", debug=True):
    return GiteaAutomated(
        solution_name=solution_name, currency=currency, expiration=expiration, wg_config=wg_config, debug=debug
    )


def deploy_cryptpad(solution_name, currency, expiration, wg_config="NO", debug=True):
    return CryptpadAutomated(
        solution_name=solution_name, currency=currency, expiration=expiration, wg_config=wg_config, debug=debug
    )


def deploy_mattermost(solution_name, currency, expiration, flavor="Silver", wg_config="NO", debug=True):
    return MattermostAutomated(
        solution_name=solution_name,
        currency=currency,
        expiration=expiration,
        flavor=flavor,
        wg_config=wg_config,
        debug=debug,
    )


def deploy_wiki(solution_name, currency, expiration, title, repo, branch, wg_config="NO", debug=True):
    return WikiAutomated(
        solution_name=solution_name,
        currency=currency,
        expiration=expiration,
        title=title,
        repo=repo,
        branch=branch,
        wg_config=wg_config,
        debug=debug,
    )


def deploy_website(solution_name, currency, expiration, title, repo, branch, wg_config="NO", debug=True):
    return WebsiteAutomated(
        solution_name=solution_name,
        currency=currency,
        expiration=expiration,
        title=title,
        repo=repo,
        branch=branch,
        wg_config=wg_config,
        debug=debug,
    )


def deploy_blog(solution_name, currency, expiration, title, repo, branch, wg_config="NO", debug=True):
    return BlogAutomated(
        solution_name=solution_name,
        currency=currency,
        expiration=expiration,
        title=title,
        repo=repo,
        branch=branch,
        wg_config=wg_config,
        debug=debug,
    )


def deploy_discourse(
    solution_name, currency, expiration, smtp_email, stmp_username, stmp_password, wg_config="NO", debug=True
):
    return DiscourseAutomated(
        solution_name=solution_name,
        currency=currency,
        expiration=expiration,
        smtp_email=smtp_email,
        stmp_username=stmp_username,
        stmp_password=stmp_password,
        wg_config=wg_config,
        debug=debug,
    )


def deploy_peertube(solution_name, currency, expiration, flavor="Silver", wg_config="NO", debug=True):
    return PeertubeAutomated(
        solution_name=solution_name,
        currency=currency,
        expiration=expiration,
        flavor=flavor,
        wg_config=wg_config,
        debug=debug,
    )


def deploy_taiga(
    solution_name, currency, expiration, smtp_email, stmp_username, stmp_password, secret, wg_config="NO", debug=True
):
    return DiscourseAutomated(
        solution_name=solution_name,
        currency=currency,
        expiration=expiration,
        smtp_email=smtp_email,
        stmp_username=stmp_username,
        stmp_password=stmp_password,
        secret=secret,
        wg_config=wg_config,
        debug=debug,
    )


def deploy_ubuntu(
    solution_name,
    version="ubuntu-18.04",
    cpu=1,
    memory=1024,
    disk_size=256,
    disk_type="SSD",
    log="NO",
    ssh="~/.ssh/id_rsa.pub",
    ipv6="NO",
    node_automatic="YES",
    node="choose_random",
    ipv4="choose_random",
    network="choose_random",
    pool="choose_random",
    debug=True,
):
    return UbuntuAutomated(
        solution_name=solution_name,
        version=version,
        cpu=cpu,
        memory=memory,
        disk_size=disk_size,
        disk_type=disk_type,
        log=log,
        ssh=ssh,
        ipv6=ipv6,
        node_automatic=node_automatic,
        node=node,
        ipv4=ipv4,
        network=network,
        pool=pool,
        debug=debug,
    )
