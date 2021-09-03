import hashlib
from io import StringIO, SEEK_END
from jumpscale.clients.explorer.models import WorkloadType


def sign_workload(workload, signing_key):
    challenge = _hash_signing_challenge(workload)
    h = _hash(challenge)
    signature = signing_key.sign(h)
    return signature.signature


def sign_provision_request(workload, tid, signing_key):
    challenge = _hash_signing_challenge(workload)

    # append the user tid to the workload signing challenge
    b = StringIO(challenge)
    b.seek(0, SEEK_END)
    b.write("provision")
    b.write(str(tid))
    h = _hash(b.getvalue())

    signature = signing_key.sign(h)

    return signature.signature


def sign_delete_request(workload, tid, signing_key):
    challenge = _hash_signing_challenge(workload)

    # append the user tid to the workload signing challenge
    b = StringIO(challenge)
    b.seek(0, SEEK_END)
    b.write("delete")
    b.write(str(tid))

    h = _hash(b.getvalue())
    signature = signing_key.sign(h)

    return signature.signature


def _hash(challenge):
    """

    Args:
      challenge:

    Returns:

    """
    if isinstance(challenge, str):
        challenge = challenge.encode("utf-8")

    h = hashlib.sha256(challenge)
    return h.digest()


def _hash_signing_challenge(workload):
    _encoders = {
        WorkloadType.Zdb: _zdb_challenge,
        WorkloadType.Container: _container_challenge,
        WorkloadType.Volume: _volume_challenge,
        # "network": _network_challenge,
        WorkloadType.Kubernetes: _k8s_challenge,
        WorkloadType.Proxy: _proxy_challenge,
        WorkloadType.Reverse_proxy: _reverse_proxy_challenge,
        WorkloadType.Subdomain: _subdomain_challenge,
        WorkloadType.Domain_delegate: _delegate_challenge,
        WorkloadType.Gateway4to6: _gateway4to6_challenge,
        WorkloadType.Network_resource: _network_resource_challenge,
        WorkloadType.Public_IP: _public_ip_challenge,
        WorkloadType.Virtual_Machine: _virtual_machine_challenge,
    }
    b = StringIO()
    b.write(_workload_info_challenge(workload.info))
    enc = _encoders.get(workload.info.workload_type)
    b.write(enc(workload))
    return b.getvalue()


def _workload_info_challenge(info):
    b = StringIO()
    b.write(str(info.workload_id))
    b.write(str(info.node_id))
    b.write(str(info.pool_id))
    b.write(str(info.reference))
    b.write(str(info.customer_tid))
    b.write(str(info.workload_type.name).upper())  # edited
    b.write(str(int(info.epoch.timestamp())))  # edited
    b.write(str(info.description))
    b.write(str(info.metadata))
    return b.getvalue()


def _signing_request_challenge(sr):
    b = StringIO()
    for s in sr.signers:
        b.write(str(s))
    b.write(str(sr.quorum_min))
    return b.getvalue()


def _signature_challenge(s):
    b = StringIO()
    b.write(str(s.tid))
    b.write(str(s.signature))
    b.write(str(s.epoch))
    return b.getvalue()


def _container_challenge(container):
    b = StringIO()
    b.write(str(container.flist))
    b.write(str(container.hub_url))
    b.write(str(container.entrypoint))
    b.write(str(container.interactive).lower())
    for k in sorted(container.environment.keys()):
        b.write(str(f"{k}={container.environment[k]}"))
    for k in sorted(container.secret_environment.keys()):
        b.write(str(f"{k}={container.secret_environment[k]}"))
    for v in container.volumes:
        b.write(str(v.volume_id))
        b.write(str(v.mountpoint))
    for nc in container.network_connection:
        b.write(str(nc.network_id))
        b.write(str(nc.ipaddress))
        b.write(str(nc.public_ip6).lower())
    b.write(str(container.capacity.cpu))
    b.write(str(container.capacity.memory))
    b.write(str(container.capacity.disk_size))
    b.write(str(container.capacity.disk_type.name).lower())  # edited. TODO: is this value or name?
    return b.getvalue()


def _volume_challenge(volume):
    b = StringIO()
    b.write(str(volume.size))
    b.write(str(volume.type.name))  # edited. TODO: is this value or name?
    return b.getvalue()


def _zdb_challenge(zdb):
    b = StringIO()
    b.write(str(zdb.size))
    b.write(str(zdb.mode.name).lower())  # edited. TODO: is this value or name?
    b.write(str(zdb.password))
    b.write(str(zdb.disk_type.name).lower())  # edited. TODO: is this value or name?
    b.write(str(zdb.public).lower())
    return b.getvalue()


def _k8s_challenge(k8s):
    b = StringIO()
    b.write(str(k8s.size))
    b.write(k8s.cluster_secret)
    b.write(k8s.network_id)
    b.write(str(k8s.ipaddress))
    for ip in k8s.master_ips:
        b.write(str(ip))
    for key in k8s.ssh_keys:
        b.write(key)
    b.write(str(k8s.public_ip))
    b.write(k8s.datastore_endpoint)
    b.write(str(k8s.disable_default_ingress).lower())
    return b.getvalue()


def _virtual_machine_challenge(vm):
    b = StringIO()
    b.write(str(vm.name))
    b.write(vm.network_id)
    b.write(str(vm.public_ip))
    b.write(str(vm.ipaddress))
    for key in vm.ssh_keys:
        b.write(key)
    b.write(str(vm.size))
    return b.getvalue()


def _proxy_challenge(proxy):
    b = StringIO()
    b.write(str(proxy.domain))
    b.write(str(proxy.addr))
    b.write(str(proxy.port))
    b.write(str(proxy.port_tls))
    return b.getvalue()


def _reverse_proxy_challenge(reverse_proxy):
    b = StringIO()
    b.write(str(reverse_proxy.domain))
    b.write(str(reverse_proxy.secret))
    return b.getvalue()


def _subdomain_challenge(subdomain):
    b = StringIO()
    b.write(str(subdomain.domain))
    for ip in subdomain.ips:
        b.write(str(ip))
    return b.getvalue()


def _delegate_challenge(delegate):
    b = StringIO()
    b.write(str(delegate.domain))
    return b.getvalue()


def _gateway4to6_challenge(gateway4to6):
    b = StringIO()
    b.write(str(gateway4to6.public_key))
    return b.getvalue()


def _network_resource_challenge(network):
    b = StringIO()
    b.write(str(network.name))
    b.write(str(network.network_iprange))
    b.write(str(network.wireguard_private_key_encrypted))
    b.write(str(network.wireguard_public_key))
    b.write(str(network.wireguard_listen_port))
    b.write(str(network.iprange))
    for p in network.peers:
        b.write(str(p.public_key))
        b.write(str(p.endpoint))
        b.write(str(p.iprange))
        for iprange in p.allowed_iprange:
            b.write(str(iprange))
    return b.getvalue()


def _public_ip_challenge(public_ip):
    b = StringIO()
    b.write(str(public_ip.ipaddress))
    return b.getvalue()
