from solutions_automation.dashboard_solutions.delegated_domain import DomainDelegationAutomated
from solutions_automation.dashboard_solutions.exposed import SolutionExposeDeployAutomated
from solutions_automation.dashboard_solutions.generic_flist import FlistAutomated
from solutions_automation.dashboard_solutions.kubernetes import KubernetesAutomated
from solutions_automation.dashboard_solutions.minio import MinioAutomated
from solutions_automation.dashboard_solutions.monitoring import MonitoringAutomated
from solutions_automation.dashboard_solutions.network import NetworkDeployAutomated
from solutions_automation.dashboard_solutions.pools import PoolAutomated
from solutions_automation.dashboard_solutions.ubuntu import UbuntuAutomated
from solutions_automation.marketplace.blog import BlogAutomated
from solutions_automation.marketplace.cryptpad import CryptpadAutomated
from solutions_automation.marketplace.discourse import DiscourseAutomated
from solutions_automation.marketplace.gitea import GiteaAutomated
from solutions_automation.marketplace.mattermost import MattermostAutomated
from solutions_automation.marketplace.peertube import PeertubeAutomated
from solutions_automation.marketplace.taiga import TaigaAutomated
from solutions_automation.marketplace.website import WebsiteAutomated
from solutions_automation.marketplace.wiki import WikiAutomated
from solutions_automation.threebot.deploy import ThreebotDeployAutomated
from solutions_automation.threebot.extend import ThreebotExtendAutomated


def deploy_gitea(solution_name, wg_config="NO", debug=True):
    return GiteaAutomated(solution_name=solution_name, wg_config=wg_config, debug=debug)


def deploy_cryptpad(solution_name, flavor="Silver", wg_config="NO", debug=True):
    return CryptpadAutomated(solution_name=solution_name, flavor=flavor, wg_config=wg_config, debug=debug,)


def deploy_mattermost(solution_name, flavor="Silver", wg_config="NO", debug=True):
    return MattermostAutomated(solution_name=solution_name, flavor=flavor, wg_config=wg_config, debug=debug,)


def deploy_wiki(solution_name, title, repo, branch, wg_config="NO", debug=True):
    return WikiAutomated(
        solution_name=solution_name, title=title, repo=repo, branch=branch, wg_config=wg_config, debug=debug,
    )


def deploy_website(solution_name, title, repo, branch, wg_config="NO", debug=True):
    return WebsiteAutomated(
        solution_name=solution_name, title=title, repo=repo, branch=branch, wg_config=wg_config, debug=debug,
    )


def deploy_blog(solution_name, title, repo, branch, wg_config="NO", debug=True):
    return BlogAutomated(
        solution_name=solution_name, title=title, repo=repo, branch=branch, wg_config=wg_config, debug=debug,
    )


def deploy_discourse(solution_name, host_email, smtp_host, host_email_password, wg_config="NO", debug=True):
    return DiscourseAutomated(
        solution_name=solution_name,
        host_email=host_email,
        smtp_host=smtp_host,
        host_email_password=host_email_password,
        wg_config=wg_config,
        debug=debug,
    )


def deploy_peertube(solution_name, flavor="Silver", wg_config="NO", debug=True):
    return PeertubeAutomated(solution_name=solution_name, flavor=flavor, wg_config=wg_config, debug=debug,)


def deploy_taiga(solution_name, host_email, smtp_host, host_email_password, secret, wg_config="NO", debug=True):
    return TaigaAutomated(
        solution_name=solution_name,
        host_email=host_email,
        smtp_host=smtp_host,
        host_email_password=host_email_password,
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


def deploy_kubernetes(
    solution_name,
    secret,
    size="1 vCPU 2 GiB ram 50GiB disk space",
    workernodes=1,
    network="choose_random",
    pools="multi_choice",
    ssh="~/.ssh/id_rsa.pub",
    debug=True,
):
    return KubernetesAutomated(
        solution_name=solution_name,
        secret=secret,
        size=size,
        workernodes=workernodes,
        network=network,
        pools=pools,
        ssh=ssh,
        debug=debug,
    )


def deploy_minio(
    solution_name,
    username,
    password,
    setup="single",
    zdb_disk_type="SSD",
    cpu=1,
    memory=1024,
    data_shards=2,
    parity_shards=1,
    network="choose_random",
    ipv4="choose_random",
    ipv6="NO",
    container_pool="choose_random",
    zdb_pools="multi_choice",
    log="NO",
    ssh="~/.ssh/id_rsa.pub",
    node_automatic="YES",
    node="choose_random",
    debug=True,
):

    return MinioAutomated(
        solution_name=solution_name,
        username=username,
        password=password,
        setup=setup,
        zdb_disk_type=zdb_disk_type,
        cpu=cpu,
        memory=memory,
        data_shards=data_shards,
        parity_shards=parity_shards,
        network=network,
        ipv4=ipv4,
        container_pool=container_pool,
        zdb_pools=zdb_pools,
        log=log,
        ssh=ssh,
        ipv6=ipv6,
        node_automatic=node_automatic,
        node=node,
        debug=debug,
    )


# TODO: uncomment after Fixing importing problem
# def deploy_4to6gw(public_key, gateway="choose_random", debug=True):
#     return FourToSixGatewayAutomated(public_key=public_key, gateway=gateway, debug=debug)


def delegated_domain(domain, gateway="choose_random", debug=True):
    return DomainDelegationAutomated(domain=domain, gateway=gateway, debug=debug)


def deploy_generic_flist(
    solution_name,
    flist,
    cpu=1,
    memory=1024,
    disk_size=256,
    vol="NO",
    corex="YES",
    entry_point="",
    env_vars={"name": "TEST"},
    log="NO",
    ipv6="NO",
    node_automatic="NO",
    node="choose_random",
    ipv4="choose_random",
    network="choose_random",
    pool="choose_random",
    debug=True,
):
    return FlistAutomated(
        solution_name=solution_name,
        flist=flist,
        cpu=cpu,
        memory=memory,
        disk_size=disk_size,
        vol=vol,
        corex=corex,
        entry_point=entry_point,
        env_vars=env_vars,
        log=log,
        ipv6=ipv6,
        node_automatic=node_automatic,
        node=node,
        ipv4=ipv4,
        network=network,
        pool=pool,
        debug=debug,
    )


def deploy_monitoring(
    solution_name,
    ssh="~/.ssh/id_rsa.pub",
    cpu=1,
    memory=1024,
    disk_size=256,
    volume_size=10,
    network="choose_random",
    redis_node_select="YES",
    redis_pool="choose_random",
    redis_ip="choose_random",
    redis_node="choose_random",
    prometheus_node_select="YES",
    prometheus_pool="choose_random",
    prometheus_ip="choose_random",
    prometheus_node="choose_random",
    grafana_node_select="YES",
    grafana_pool="choose_random",
    grafana_ip="choose_random",
    grafana_node="choose_random",
    debug=True,
):
    return MonitoringAutomated(
        solution_name=solution_name,
        ssh=ssh,
        cpu=cpu,
        memory=memory,
        disk_size=disk_size,
        volume_size=volume_size,
        network=network,
        redis_node_select=redis_node_select,
        redis_pool=redis_pool,
        redis_ip=redis_ip,
        redis_node=redis_node,
        prometheus_node_select=prometheus_node_select,
        prometheus_pool=prometheus_pool,
        prometheus_ip=prometheus_ip,
        prometheus_node=prometheus_node,
        grafana_node_select=grafana_node_select,
        grafana_pool=grafana_pool,
        grafana_ip=grafana_ip,
        grafana_node=grafana_node,
        debug=True,
    )


def create_network(
    solution_name,
    ip_version="IPv4",
    ip_select="Choose ip range for me",
    ip_range="",
    access_node="choose_random",
    pool="choose_random",
    debug=True,
):
    return NetworkDeployAutomated(
        solution_name=solution_name,
        type="Create",
        ip_version=ip_version,
        ip_select=ip_select,
        ip_range=ip_range,
        access_node=access_node,
        pool=pool,
        debug=True,
    )


def add_access_to_network(
    network_name, ip_version="IPv4", debug=True,
):
    return NetworkDeployAutomated(network_name=network_name, type="Add Access", ip_version=ip_version, debug=True,)


def deploy_exposed(
    type,
    solution_to_expose,
    sub_domain,
    domain="choose_random",
    tls_port=6443,
    port=6443,
    debug=True,
    proxy_type="TRC",
    force_https="NO",
):
    return SolutionExposeDeployAutomated(
        type=type,
        solution_to_expose=solution_to_expose,
        domain=domain,
        sub_domain=sub_domain,
        tls_port=tls_port,
        port=port,
        debug=debug,
        proxy_type=proxy_type,
        force_https=force_https,
    )


def create_pool(
    solution_name, wallet_name, farm="choose_random", cu=1, su=1, time_unit="Day", time_to_live=1, debug=True,
):
    return PoolAutomated(
        type="create",
        solution_name=solution_name,
        wallet_name=wallet_name,
        farm=farm,
        cu=cu,
        su=su,
        time_unit=time_unit,
        time_to_live=time_to_live,
        debug=debug,
    )


def extend_pool(
    pool_name, wallet_name, farm="choose_random", cu=1, su=1, time_unit="Day", time_to_live=1, debug=True,
):
    return PoolAutomated(
        type="extend",
        pool_name=pool_name,
        wallet_name=wallet_name,
        farm=farm,
        cu=cu,
        su=su,
        time_unit=time_unit,
        time_to_live=time_to_live,
        debug=debug,
    )


def deploy_threebot(
    solution_name,
    ssh,
    secret,
    expiration,
    debug=True,
    domain_type="Automatically Get a Domain",
    domain_name=None,
    public_key="",
):
    return ThreebotDeployAutomated(
        type="Create",
        solution_name=solution_name,
        secret=secret,
        expiration=expiration,
        debug=debug,
        domain_type=domain_type,
        domain_name=domain_name,
        public_key=public_key,
    )


def recover_threebot(solution_name, recover_password, ssh, expiration, debug=True):
    return ThreebotDeployAutomated(
        type="Recover",
        solution_name=solution_name,
        recover_password=recover_password,
        ssh=ssh,
        expiration=expiration,
        debug=debug,
    )


def extend_threebot(name, expiration):
    return ThreebotExtendAutomated(name=name, expiration=expiration)
