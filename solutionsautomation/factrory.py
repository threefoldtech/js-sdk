from gitea import GiteaAutomated
from cryptpad import CryptpadAutomated
from wiki import WikiAutomated
from website import WebsiteAutomated
from blog import BlogAutomated
from ubuntu import UbuntuAutomated
from mattermost import MattermostAutomated
from discourse import DiscourseAutomated
from peertube import PeertubeAutomated
from kubernetes import KubernetesAutomated
from minio import MinioAutomated
from four_to6gw import FourToSixGatewayAutomated
from delegated_domain import DomainDelegationAutomated
from generic_flist import FlistAutomated
from monitoring import MonitoringAutomated
from network import NetworkDeployAutomated
from taiga import TaigaAutomated
from exposed import SolutionExposeDeployAutomated
from pools import PoolAutomated
from threebot_deploy import ThreebotDeployAutomated


def deploy_gitea(solution_name, currency, expiration, wg_config="NO", debug=True):
    return GiteaAutomated(
        solution_name=solution_name, currency=currency, expiration=expiration, wg_config=wg_config, debug=debug
    )


def deploy_cryptpad(solution_name, currency, expiration, flavor="Silver", wg_config="NO", debug=True):
    return CryptpadAutomated(
        solution_name=solution_name,
        currency=currency,
        expiration=expiration,
        flavor=flavor,
        wg_config=wg_config,
        debug=debug,
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
    return TaigaAutomated(
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
    container_pool="choose_random",
    zdb_pools="multi_choice",
    log="NO",
    ssh="~/.ssh/id_rsa.pub",
    ipv6="NO",
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


def deploy_4to6gw(public_key, debug=True):
    return FourToSixGatewayAutomated(public_key=public_key, debug=debug)


def delegated_domain(solution_name, debug=True):
    return DomainDelegationAutomated(solution_name=solution_name, debug=debug)


def deploy_generic_flist(
    solution_name,
    currency="TFT",
    flist="https://hub.grid.tf/tf-bootable/3bot-ubuntu-18.04.flist",
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
    debug=True,
):
    return FlistAutomated(
        solution_name=solution_name,
        currency=currency,
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
        debug=debug,
    )


def deploy_monitoring(
    solution_name,
    currency="TFT",
    ssh="~/.ssh/id_rsa.pub",
    cpu=1,
    memory=1024,
    disk_size=256,
    volume_size=10,
    redis_node_select="yes",
    prometheus_node_select="yes",
    grafana_node_select="yes",
    debug=True,
):
    return MonitoringAutomated(
        solution_name=solution_name,
        currency=currency,
        ssh=ssh,
        cpu=cpu,
        memory=memory,
        disk_size=disk_size,
        volume_size=volume_size,
        redis_node_select=redis_node_select,
        prometheus_node_select=prometheus_node_select,
        grafana_node_select=grafana_node_select,
        debug=True,
    )


def deploy_network(
    solution_name, type, ip_type="IPv4", network_ip="Choose ip range for me", debug=True,
):
    return NetworkDeployAutomated(
        solution_name=solution_name, type=type, ip_type=ip_type, network_ip=network_ip, debug=True,
    )


def deploy_exposed(
    type, tls_port=6443, port_expose=6443, sub_domain="subdomain3", debug=True,
):
    return SolutionExposeDeployAutomated(
        type=type, tls_port=tls_port, port_expose=port_expose, sub_domain=sub_domain, debug=debug
    )


def deploy_pool(
    type, solution_name, wallet_name, cu=1, su=1, time_unit="Day", time_to_live=1, debug=True,
):
    return PoolAutomated(
        type=type,
        solution_name=solution_name,
        wallet_name=wallet_name,
        cu=cu,
        su=su,
        time_unit=time_unit,
        time_to_live=time_to_live,
        debug=debug,
    )


def deploy_threebot(type, solution_name, secret, expiration, debug=True):
    return ThreebotDeployAutomated(
        type=type, solution_name=solution_name, secret=secret, expiration=expiration, debug=debug
    )
