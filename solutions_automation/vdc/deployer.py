from solutions_automation.vdc.dashboard.vdc import VDCAutomated
from solutions_automation.vdc.dashboard.blog import BlogAutomated
from solutions_automation.vdc.dashboard.cryptpad import CryptpadAutomated
from solutions_automation.vdc.dashboard.digibyte import DigibyteAutomated
from solutions_automation.vdc.dashboard.discourse import DiscourseAutomated
from solutions_automation.vdc.dashboard.etcd import EtcdAutomated
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


def deploy_vdc(solution_name, vdc_secert, vdc_plan):
    return VDCAutomated(
        solution_name=solution_name, vdc_secert=vdc_secert, vdc_plan=vdc_plan, zdb_Farms="Automatically Select Farms"
    )


def deploy_blog(
    release_name,
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
        url=url,
        branch=branch,
        sub_domain=sub_domain,
        custom_sub_domain=custom_sub_domain,
        debug=debug,
    )


def deploy_cryptpad(
    release_name,
    storage_size="10",
    flavor="Silver",
    sub_domain="Choose subdomain for me on a gateway",
    custom_sub_domain="",
    debug=True,
):
    return CryptpadAutomated(
        release_name=release_name,
        storage_size=storage_size,
        flavor=flavor,
        sub_domain=sub_domain,
        custom_sub_domain=custom_sub_domain,
        debug=debug,
    )


def deploy_digibyte(
    release_name,
    rpc_username,
    rpc_password,
    flavor="Silver",
    sub_domain="Choose subdomain for me on a gateway",
    custom_sub_domain="",
    debug=True,
):
    return DigibyteAutomated(
        release_name=release_name,
        rpc_username=rpc_username,
        rpc_password=rpc_password,
        flavor=flavor,
        sub_domain=sub_domain,
        custom_sub_domain=custom_sub_domain,
        debug=True,
    )


def deploy_discourse(
    release_name,
    admin_username,
    admin_password,
    smtp_host,
    smtp_port,
    smtp_username,
    smtp_password,
    flavor="Silver",
    sub_domain="Choose subdomain for me on a gateway",
    custom_sub_domain="",
    debug=True,
):
    return DiscourseAutomated(
        release_name=release_name,
        admin_username=admin_username,
        admin_password=admin_password,
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        smtp_username=smtp_username,
        smtp_password=smtp_password,
        flavor=flavor,
        sub_domain=sub_domain,
        custom_sub_domain=custom_sub_domain,
        debug=debug,
    )


def deploy_etcd(
    release_name, flavor="Silver", sub_domain="Choose subdomain for me on a gateway", custom_sub_domain="", debug=True
):
    return EtcdAutomated(
        release_name=release_name,
        flavor=flavor,
        sub_domain=sub_domain,
        custom_sub_domain=custom_sub_domain,
        debug=debug,
    )


def extend_kubernetes(size, existing_balance="Yes", debug=True):
    return ExtendKubernetesAutomated(size=size, existing_balance=existing_balance, debug=debug)


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
        url=url,
        branch=branch,
        src_dir=src_dir,
        sub_domain=sub_domain,
        custom_sub_domain=custom_sub_domain,
        debug=debug,
    )


def deploy_wiki(
    release_name,
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
