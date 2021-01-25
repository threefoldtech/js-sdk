from solutions_automation.vdc.dashboard.blog import BlogAutomated
from solutions_automation.vdc.dashboard.cryptpad import CryptpadAutomated
from solutions_automation.vdc.dashboard.discourse import DiscourseAutomated
from solutions_automation.vdc.dashboard.extend_kubernetes import ExtendKubernetesAutomated
from solutions_automation.vdc.dashboard.gitea import GiteaAutomated
from solutions_automation.vdc.dashboard.kubeapps import KubeappsAutomated
from solutions_automation.vdc.dashboard.mattermost import MattermostAutomated
from solutions_automation.vdc.dashboard.monitoring import MonitoringStackAutomated
from solutions_automation.vdc.dashboard.peertube import PeertubeAutomated
from solutions_automation.vdc.dashboard.taiga import TaigaAutomated
from solutions_automation.vdc.dashboard.website import WebsiteAutomated
from solutions_automation.vdc.dashboard.wiki import WikiAutomated
from solutions_automation.vdc.dashboard.zeroci import ZeroCIAutomated


def deploy_blog(
    release_name,
    title,
    url,
    branch,
    flavor="Silver",
    sub_domain="Choose subdomain for me on a gateway",
    custom_sub_domain="",
    debug=True,
):
    return BlogAutomated(
        release_name=release_name,
        flavor=flavor,
        title=title,
        url=url,
        branch=branch,
        sub_domain=sub_domain,
        custom_sub_domain=custom_sub_domain,
        debug=debug,
    )


def deploy_cryptpad(
    release_name, flavor="Silver", sub_domain="Choose subdomain for me on a gateway", custom_sub_domain="", debug=True
):
    return CryptpadAutomated(
        release_name=release_name,
        flavor=flavor,
        sub_domain=sub_domain,
        custom_sub_domain=custom_sub_domain,
        debug=debug,
    )


def deploy_discourse(
    release_name, flavor="Silver", sub_domain="Choose subdomain for me on a gateway", custom_sub_domain="", debug=True
):
    return DiscourseAutomated(
        release_name=release_name,
        flavor=flavor,
        sub_domain=sub_domain,
        custom_sub_domain=custom_sub_domain,
        debug=debug,
    )


def deploy_extend_kubernetes(release_name, size, debug=True):
    return ExtendKubernetesAutomated(release_name=release_name, size=size, debug=debug)


def deploy_gitea(
    release_name, flavor="Silver", sub_domain="Choose subdomain for me on a gateway", custom_sub_domain="", debug=True
):
    return GiteaAutomated(
        release_name=release_name,
        flavor=flavor,
        sub_domain=sub_domain,
        custom_sub_domain=custom_sub_domain,
        debug=debug,
    )


def deploy_kubeapps(
    release_name, flavor="Silver", sub_domain="Choose subdomain for me on a gateway", custom_sub_domain="", debug=True
):
    return KubeappsAutomated(
        release_name=release_name,
        flavor=flavor,
        sub_domain=sub_domain,
        custom_sub_domain=custom_sub_domain,
        debug=debug,
    )


def deploy_mattermost(
    release_name,
    mysql_username,
    mysql_password,
    mysql_root_password,
    flavor="Silver",
    sub_domain="Choose subdomain for me on a gateway",
    custom_sub_domain="",
    debug=True,
):
    return MattermostAutomated(
        release_name=release_name,
        flavor=flavor,
        mysql_username=mysql_username,
        mysql_password=mysql_password,
        mysql_root_password=mysql_root_password,
        sub_domain=sub_domain,
        custom_sub_domain=custom_sub_domain,
        debug=debug,
    )


def deploy_monitoring(
    release_name, flavor="Silver", sub_domain="Choose subdomain for me on a gateway", custom_sub_domain="", debug=True
):
    return MonitoringStackAutomated(
        release_name=release_name,
        flavor=flavor,
        sub_domain=sub_domain,
        custom_sub_domain=custom_sub_domain,
        debug=debug,
    )


def deploy_peertube(
    release_name, flavor="Silver", sub_domain="Choose subdomain for me on a gateway", custom_sub_domain="", debug=True
):
    return PeertubeAutomated(
        release_name=release_name,
        flavor=flavor,
        sub_domain=sub_domain,
        custom_sub_domain=custom_sub_domain,
        debug=debug,
    )


def deploy_taiga(
    release_name, flavor="Silver", sub_domain="Choose subdomain for me on a gateway", custom_sub_domain="", debug=True
):
    return TaigaAutomated(
        release_name=release_name,
        flavor=flavor,
        sub_domain=sub_domain,
        custom_sub_domain=custom_sub_domain,
        debug=debug,
    )


def deploy_website(
    release_name,
    title,
    url,
    branch,
    src_dir="html",
    flavor="Silver",
    sub_domain="Choose subdomain for me on a gateway",
    custom_sub_domain="",
    debug=True,
):
    return WebsiteAutomated(
        release_name=release_name,
        flavor=flavor,
        title=title,
        url=url,
        branch=branch,
        src_dir=src_dir,
        sub_domain=sub_domain,
        custom_sub_domain=custom_sub_domain,
        debug=debug,
    )


def deploy_wiki(
    release_name,
    title,
    url,
    branch,
    src_dir="src",
    flavor="Silver",
    sub_domain="Choose subdomain for me on a gateway",
    custom_sub_domain="",
    debug=True,
):
    return WikiAutomated(
        release_name=release_name,
        flavor=flavor,
        title=title,
        url=url,
        branch=branch,
        src_dir=src_dir,
        sub_domain=sub_domain,
        custom_sub_domain=custom_sub_domain,
        debug=debug,
    )


def deploy_zeroci(
    release_name, flavor="Silver", sub_domain="Choose subdomain for me on a gateway", custom_sub_domain="", debug=True
):
    return ZeroCIAutomated(
        release_name=release_name,
        flavor=flavor,
        sub_domain=sub_domain,
        custom_sub_domain=custom_sub_domain,
        debug=debug,
    )
