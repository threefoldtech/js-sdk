import random
import uuid
import os

import gevent
from jumpscale.clients.explorer.models import NextAction, WorkloadType
from jumpscale.loader import j
from jumpscale.sals.reservation_chatflow import deployer
from jumpscale.sals.reservation_chatflow.deployer import DeploymentFailed

from .base_component import VDCBaseComponent
from .scheduler import Scheduler
from textwrap import dedent

VDC_PARENT_DOMAIN = j.core.config.get("VDC_PARENT_DOMAIN", "grid.tf")

PROXY_SERVICE_TEMPLATE = """
kind: Service
apiVersion: v1
metadata:
 name: {{ service_name }}
spec:
 type: ClusterIP
 ports:
 - port: {{ port }}
"""


PROXY_ENDPOINT_TEMPLATE = """
kind: Endpoints
apiVersion: v1
metadata:
 name: {{ endpoint_name }}
subsets:
 - addresses:
    {% for address in addresses %}
     - ip: {{ address }}
    {% endfor %}
   ports:
     - port: {{ port }}
"""


PROXY_INGRESS_TEMPLATE = """
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: {{ ingress_name }}
  {% if force_https %}
  annotations:
    ingress.kubernetes.io/ssl-redirect: "true"
  {% endif %}
spec:
  rules:
    - host: {{ hostname }}
      http:
        paths:
        - path: /
          backend:
            serviceName: {{ service_name }}
            servicePort: {{ service_port }}
"""


class VDCProxy(VDCBaseComponent):
    def __init__(self, vdc_deployer, farm_name=None):
        super().__init__(vdc_deployer)
        self._farm_name = farm_name
        self._farm = None

    @property
    def farm(self):
        if not self._farm:
            self._farm = self.explorer.farms.get(farm_name=self.farm_name)
        return self._farm

    @property
    def farm_name(self):
        if not self._farm_name:
            gateways = self.explorer.gateway.list()
            random.shuffle(gateways)
            for gateway in gateways:
                if not self.zos.nodes_finder.filter_is_up(gateway):
                    continue
                if not gateway.dns_nameserver:
                    continue
                if not gateway.farm_id:
                    continue
                farm_id = gateway.farm_id
                try:
                    farm = self.explorer.farms.get(farm_id)
                    self._farm_name = farm.name
                    return self._farm_name
                except Exception as e:
                    self.vdc_deployer.error(f"failed to fetch farm with id {farm_id} due to error {str(e)}")
                    continue
            raise j.exceptions.Runtime("couldn't find any running gateway")

        return self._farm_name

    def fetch_myfarm_gateways(self):
        farm_gateways = []
        for gateway in self.explorer.gateway.list(farm_id=self.farm.id):
            if not self.zos.nodes_finder.filter_is_up(gateway):
                continue
            if not gateway.dns_nameserver:
                continue
            farm_gateways.append(gateway)
        return farm_gateways

    def get_gateway_pool_id(self):
        """
        return a pool id on my farm that has available gateway
        """
        self.vdc_deployer.info(f"looking for pool with gateways within farm: {self.farm_name}")
        farm_gateways = self.fetch_myfarm_gateways()
        if not farm_gateways:
            self.vdc_deployer.error(f"no gateways available in farm: {self.farm_name}")
            return

        self.vdc_deployer.info(f"looking for existing pools that contain gateways of farm: {self.farm_name}")
        gateway_node_ids = [node.node_id for node in farm_gateways]
        for pool in self.zos.pools.list():
            if list(set(pool.node_ids) & set(gateway_node_ids)):
                self.vdc_deployer.info(
                    f"found pool with available gateways on farm: {self.farm_name} pool_id: {pool.pool_id}"
                )
                return pool.pool_id

        self.vdc_deployer.info(f"reserving an empty pool on farm: {self.farm_name}")
        # no pool was found need to create a pool
        pool_info = self.zos.pools.create(0, 0, 0, self.farm_name)
        self.vdc_deployer.info(f"gateway pool: {pool_info.reservation_id}")
        return pool_info.reservation_id

    def get_gateway_addresses(self, gateway):
        addresses = []
        for nameserver in gateway.dns_nameserver:
            try:
                self.vdc_deployer.info(f"resolving name: {nameserver} of gateway {gateway.node_id}")
                addresses.append(j.sals.nettools.get_host_by_name(nameserver))
            except Exception as e:
                self.vdc_deployer.error(
                    f"failed to resolve dns: {nameserver} of gateway {gateway.node_id} due to error {str(e)}"
                )
                continue
        return addresses

    @staticmethod
    def check_domain_availability(domain):
        try:
            ip = j.sals.nettools.get_host_by_name(domain)
            if ip:
                return True
        except:
            return False

    def wait_domain_population(self, domain, timeout=5):
        end = j.data.time.now().timestamp + timeout * 60
        while j.data.time.now().timestamp < end:
            if self.check_domain_availability(domain):
                return True
            gevent.sleep(3)
        return False

    def check_subdomain_existence(self, subdomain, workloads=None):
        self.vdc_deployer.info(f"checking the ownership of subdomain {subdomain}")
        workloads = workloads or self.zos.workloads.list(self.identity.tid, NextAction.DEPLOY)
        # get the latest workload that represents this domain
        old_workloads = []
        latest_domain_workload = None
        for workload in workloads:
            if workload.info.workload_type != WorkloadType.Subdomain:
                continue
            if workload.domain != subdomain:
                continue
            old_workloads.append(workload)
            latest_domain_workload = workload
        if len(old_workloads) > 1:
            old_workloads.pop(-1)
            self.vdc_deployer.info(
                f"Cancelling old workloads for subdomain: {subdomain} wids: {[workload.id for workload in old_workloads]}"
            )
            for workload in old_workloads:
                self.zos.decomission(workload.id)
            for workload in old_workloads:
                deployer.wait_workload_deletion(workload.id, identity_name=self.identity.instance_name)
        return latest_domain_workload

    def verify_subdomain(self, subdomain_workload, addresses=None):
        gateway = self.explorer.gateway.get(subdomain_workload.info.node_id)
        addresses = addresses or self.get_gateway_addresses(gateway)
        self.vdc_deployer.info(
            f"verifying subdomain workload: {subdomain_workload.id} ips: {subdomain_workload.ips} matching addresses {addresses}"
        )
        if set(addresses.sort()) == set(subdomain_workload.ips.sort()):
            self.vdc_deployer.info(f"subdomain {subdomain_workload.id} matching addresses {addresses}")
            return True
        self.vdc_deployer.info(f"Cancelling subdomain workload {subdomain_workload.id}")
        self.zos.workloads.decomission(subdomain_workload.id)
        deployer.wait_workload_deletion(subdomain_workload.id, identity_name=self.identity.instance_name)
        return False

    def check_subdomain_owner(self, subdomain):
        e = self.zos._explorer
        users = e.users.list()
        uids = [u.id for u in users]
        for uid in uids:
            workloads = e.workloads.list_workloads(uid, next_action="DEPLOY")
            for w in workloads:
                if w.info.workload_type != WorkloadType.Subdomain:
                    continue
                if w.domain == subdomain:
                    return uid

    def reserve_subdomain(self, gateway, prefix, vdc_uuid, pool_id=None, ip_address=None, exposed_wid=None):
        """
        it will try to create a working subdomain on any of the available managed domain of the gateway
        Args:
            gateway: gateway to use
            prefix: the prefix that will be added to the managed domain
            ip_address: which the subdomain will point to. by default will point to the chosen gateway

        yields:
            subdomain
            workload id
        """
        desc = j.data.serializers.json.loads(self.vdc_deployer.description)
        desc["exposed_wid"] = exposed_wid
        desc = j.data.serializers.json.dumps(desc)
        pool_id = pool_id or self.get_gateway_pool_id()
        if not pool_id:
            return None

        for managed_domain in gateway.managed_domains:
            self.vdc_deployer.info(f"reserving subdomain of {managed_domain}")
            # vdc 3bot to be vdctest.grid.tf, solutions to be webg1test.grid.tf or alike
            if not managed_domain.startswith("vdc"):
                continue
            subdomain = f"{prefix}.{managed_domain}"
            addresses = None

            # check availability of the subdomain
            if self.check_domain_availability(subdomain):
                self.vdc_deployer.info(f"subdomain {subdomain} already exists")
                # check if the subdomain is owned by me
                self.vdc_deployer.info(f"checking if subdomain {subdomain} is owned by identity {self.identity.tid}")
                subdomain_workload = self.check_subdomain_existence(subdomain)
                if not subdomain_workload:
                    # subdomain is not mine, get a new one
                    self.vdc_deployer.info(f"checking if subdomain {subdomain} is deployed on the explorer")
                    owner_id = self.check_subdomain_owner(subdomain)
                    if owner_id:
                        self.vdc_deployer.error(
                            f"subdomain {subdomain} exists and not owned by VDC identity {self.identity.tid}. Subdomain owner id: {owner_id}"
                        )
                        continue
                # verify the subdomain is pointing to the correct address or cancel it
                valid = self.verify_subdomain(subdomain_workload, addresses)
                if valid:
                    # use the subdomain
                    yield subdomain, subdomain_workload.id
                    # check the next managed domain
                    continue

            if ip_address:
                addresses = [ip_address]
            else:
                addresses = self.get_gateway_addresses(gateway)
            # check resolvable names of the gateway dns servers
            if not addresses:
                self.vdc_deployer.error(f"gateway {gateway.node_id} doesn't have any valid nameservers configured")
                break
            # check population of the managed domain
            if not deployer.test_managed_domain(
                gateway.node_id, managed_domain, pool_id, gateway, self.identity.instance_name
            ):
                self.vdc_deployer.error(
                    f"population of managed domain {managed_domain} failed on gateway {gateway.node_id}"
                )
                continue

            # reserve subdomain
            wid = deployer.create_subdomain(
                pool_id,
                gateway.node_id,
                subdomain,
                addresses,
                identity_name=self.identity.instance_name,
                solution_uuid=vdc_uuid,
                exposed_wid=exposed_wid,
                description=desc,
            )
            try:
                success = deployer.wait_workload(
                    wid, bot=self.bot, identity_name=self.identity.instance_name, cancel_by_uuid=False
                )
                if not success:
                    raise DeploymentFailed()
            except DeploymentFailed:
                self.vdc_deployer.error(f"Subdomain {subdomain} failed. wid: {wid}")
                continue

            populated = self.wait_domain_population(subdomain)
            if populated:
                self.vdc_deployer.info(f"Subdomain {subdomain} created successfully pointing to {addresses}")
                yield subdomain, wid
            else:
                self.vdc_deployer.error(f"Subdomain {subdomain} failed to populate wid: {wid}")
                self.zos.workloads.decomission(wid)
        self.vdc_deployer.error(f"All attempts to reserve a subdomain failed on farm {self.farm_name}")

    def _deploy_nginx_proxy(
        self,
        scheduler,
        wid,
        subdomain,
        gateway,
        pool_id,
        secret,
        ip_address,
        port,
        gateway_pool_id,
        solution_uuid,
        description,
    ):
        # proxy the conainer
        cont_id = None
        proxy_id = None
        for node in scheduler.nodes_by_capacity(cru=1, mru=1, sru=0.25):
            try:
                self.vdc_deployer.info(
                    f"deploying nginx proxy for wid: {wid} on node: {node.node_id} subdomain: {subdomain} gateway: {gateway.node_id}"
                )
                cont_id, proxy_id = deployer.expose_and_create_certificate(
                    pool_id=pool_id,
                    gateway_id=gateway.node_id,
                    network_name=self.vdc_name,
                    trc_secret=secret,
                    domain=subdomain,
                    email=self.vdc_deployer.email,
                    solution_ip=ip_address,
                    solution_port=port,
                    enforce_https=True,
                    proxy_pool_id=gateway_pool_id,
                    bot=self.bot,
                    solution_uuid=solution_uuid,
                    secret=secret,
                    node_id=node.node_id,
                    exposed_wid=wid,
                    identity_name=self.identity.instance_name,
                    public_key=self.vdc_deployer.ssh_key.public_key.strip(),
                    description=description,
                )
                success = deployer.wait_workload(
                    cont_id, self.bot, identity_name=self.identity.instance_name, cancel_by_uuid=False
                )
                if not success:
                    self.vdc_deployer.error(
                        f"Nginx container for wid: {wid} failed on node: {node.node_id}, nginx_wid: {cont_id}"
                    )
                    # container only failed. no need to decomission subdomain
                    self.zos.workloads.decomission(proxy_id)
                    continue
                return subdomain
            except DeploymentFailed:
                self.vdc_deployer.error(
                    f"Proxy reservation for wid: {wid} failed on node: {node.node_id}, subdomain: {subdomain}, gateway: {gateway.node_id}"
                )
                if cont_id:
                    self.zos.workloads.decomission(cont_id)
                if proxy_id:
                    self.zos.workloads.decomission(proxy_id)
                continue

    def _deploy_trc_proxy(
        self,
        scheduler,
        wid,
        subdomain,
        gateway,
        pool_id,
        secret,
        ip_address,
        port,
        tls_port,
        gateway_pool_id,
        solution_uuid,
        description,
    ):
        cont_id = None
        proxy_id = None
        for node in scheduler.nodes_by_capacity(cru=1, mru=1, sru=0.25):
            try:
                self.vdc_deployer.info(
                    f"Deploying trc proxy for wid: {wid} on node: {node.node_id} subdomain: {subdomain} gateway: {gateway.node_id}"
                )
                cont_id, proxy_id = deployer.expose_address(
                    reserve_proxy=True,
                    pool_id=pool_id,
                    gateway_id=gateway.node_id,
                    network_name=self.vdc_name,
                    trc_secret=secret,
                    domain_name=subdomain,
                    local_ip=ip_address,
                    port=port,
                    tls_port=tls_port,
                    proxy_pool_id=gateway_pool_id,
                    bot=self.bot,
                    solution_uuid=solution_uuid,
                    node_id=node.node_id,
                    exposed_wid=wid,
                    identity_name=self.identity.instance_name,
                    description=description,
                )
                success = deployer.wait_workload(
                    cont_id, self.bot, identity_name=self.identity.instance_name, cancel_by_uuid=False
                )
                if not success:
                    self.vdc_deployer.error(
                        f"Nginx container for wid: {wid} failed on node: {node.node_id}, nginx_wid: {cont_id}"
                    )
                    # container only failed. no need to decomission subdomain
                    self.zos.workloads.decomission(proxy_id)
                    continue
                return subdomain
            except DeploymentFailed:
                self.vdc_deployer.error(
                    f"proxy reservation for wid: {wid} failed on node: {node.node_id}, subdomain: {subdomain}, gateway: {gateway.node_id}"
                )
                if cont_id:
                    self.zos.workloads.decomission(cont_id)
                if proxy_id:
                    self.zos.workloads.decomission(proxy_id)
                continue

    def proxy_container_over_custom_domain(
        self,
        prefix,
        wid,
        port,
        solution_uuid,
        pool_id=None,
        secret=None,
        scheduler=None,
        tls_port=None,
        parent_domain=None,
    ):
        """
        Args:
            prefix: MUST BE UNIQUE will be appended to parent domain (vdc.grid.tf) if it already exist it will be deleted and recreated
            wid: workload id of the container to expose
        """
        parent_domain = parent_domain or VDC_PARENT_DOMAIN
        subdomain = f"{prefix}.{parent_domain}"
        nc = j.clients.name.get("VDC")
        nc.username = os.environ.get("VDC_NAME_USER")
        nc.token = os.environ.get("VDC_NAME_TOKEN")

        secret = secret or uuid.uuid4().hex
        secret = f"{self.identity.tid}:{secret}"
        scheduler = scheduler or Scheduler(self.farm_name)
        workload = self.zos.workloads.get(wid)
        if workload.info.workload_type != WorkloadType.Container:
            raise j.exceptions.Validation(f"can't expose workload {wid} of type {workload.info.workload_type}")

        pool_id = pool_id or workload.info.pool_id
        ip_address = workload.network_connection[0].ipaddress
        self.vdc_deployer.info(f"proxy container {wid} ip: {ip_address} port: {port} pool: {pool_id}")
        gateways = self.fetch_myfarm_gateways()
        random.shuffle(gateways)
        gateway_pool_id = self.get_gateway_pool_id()
        desc = j.data.serializers.json.loads(self.vdc_deployer.description)
        desc["exposed_wid"] = wid
        desc = j.data.serializers.json.dumps(desc)
        for gateway in gateways:
            # if old records exist for this prefix clean it.
            existing_records = nc.nameclient.list_records_for_host(parent_domain, prefix)
            if existing_records:
                for record_dict in existing_records:
                    nc.nameclient.delete_record(record_dict["fqdn"][:-1], record_dict["id"])

            # create a subdomain in domain provider that points to the gateway
            ip_addresses = self.get_gateway_addresses(gateway)
            for address in ip_addresses:
                nc.nameclient.create_record(parent_domain, prefix, "A", address)
            if not tls_port:
                result = self._deploy_nginx_proxy(
                    scheduler,
                    wid,
                    subdomain,
                    gateway,
                    pool_id,
                    secret,
                    ip_address,
                    port,
                    gateway_pool_id,
                    solution_uuid,
                    desc,
                )
            else:
                result = self._deploy_trc_proxy(
                    scheduler,
                    wid,
                    subdomain,
                    gateway,
                    pool_id,
                    secret,
                    ip_address,
                    port,
                    tls_port,
                    gateway_pool_id,
                    solution_uuid,
                    desc,
                )
            if result:
                return result
            scheduler.refresh_nodes()

    def proxy_container_over_managed_domain(
        self, prefix, wid, port, solution_uuid, pool_id=None, secret=None, scheduler=None, tls_port=None
    ):
        secret = secret or uuid.uuid4().hex
        secret = f"{self.identity.tid}:{secret}"
        scheduler = scheduler or Scheduler(self.farm_name)
        workload = self.zos.workloads.get(wid)
        if workload.info.workload_type != WorkloadType.Container:
            raise j.exceptions.Validation(f"can't expose workload {wid} of type {workload.info.workload_type}")

        pool_id = pool_id or workload.info.pool_id
        ip_address = workload.network_connection[0].ipaddress
        self.vdc_deployer.info(f"proxy container {wid} ip: {ip_address} port: {port} pool: {pool_id}")
        gateways = self.fetch_myfarm_gateways()
        random.shuffle(gateways)
        gateway_pool_id = self.get_gateway_pool_id()
        desc = j.data.serializers.json.loads(self.vdc_deployer.description)
        desc["exposed_wid"] = wid
        desc = j.data.serializers.json.dumps(desc)
        for gateway in gateways:
            for subdomain, subdomain_id in self.reserve_subdomain(
                gateway, prefix, solution_uuid, gateway_pool_id, exposed_wid=wid
            ):
                if not tls_port:
                    result = self._deploy_nginx_proxy(
                        scheduler,
                        wid,
                        subdomain,
                        gateway,
                        pool_id,
                        secret,
                        ip_address,
                        port,
                        gateway_pool_id,
                        solution_uuid,
                        desc,
                    )
                else:
                    result = self._deploy_trc_proxy(
                        scheduler,
                        wid,
                        subdomain,
                        gateway,
                        pool_id,
                        secret,
                        ip_address,
                        port,
                        tls_port,
                        gateway_pool_id,
                        solution_uuid,
                        desc,
                    )
                if result:
                    return result
                self.zos.workloads.decomission(subdomain_id)
                self.vdc_deployer.error(f"failed to proxy wid: {wid} on subdomain {subdomain}")
                scheduler.refresh_nodes()
            self.vdc_deployer.error(f"failed to expose workload {wid} on gateway {gateway.node_id}")
        self.vdc_deployer.error(f"All attempts to expose wid {wid} failed")

    def ingress_proxy_over_custom_domain(
        self, name, prefix, port, public_ip, private_ip=None, wid=None, parent_domain=None, force_https=True
    ):
        if not any([private_ip, wid]):
            raise j.exceptions.Input(f"must pass private ip or wid")
        parent_domain = parent_domain or VDC_PARENT_DOMAIN
        subdomain = f"{prefix}.{parent_domain}"
        nc = j.clients.name.get("VDC")
        nc.username = os.environ.get("VDC_NAME_USER")
        nc.token = os.environ.get("VDC_NAME_TOKEN")

        if not private_ip:
            workload = self.zos.workloads.get(wid)
            if workload.info.workload_type != WorkloadType.Container:
                raise j.exceptions.Validation(f"can't expose workload {wid} of type {workload.info.workload_type}")
            ip_address = workload.network_connection[0].ipaddress
        else:
            ip_address = private_ip

        self.vdc_deployer.info(
            f"ingress proxy over custom domain: {subdomain}, name: {name}, ip_address: {ip_address}, public_ip: {public_ip}"
        )

        # if old records exist for this prefix clean it.
        existing_records = nc.nameclient.list_records_for_host(parent_domain, prefix)
        if existing_records:
            for record_dict in existing_records:
                nc.nameclient.delete_record(record_dict["fqdn"][:-1], record_dict["id"])

        # create a subdomain in domain provider that points to the gateway
        nc.nameclient.create_record(parent_domain, prefix, "A", public_ip)
        self._create_ingress(name, subdomain, [ip_address], port, force_https)
        return subdomain

    def ingress_proxy_over_managed_domain(self, name, prefix, wid, port, public_ip, solution_uuid, force_https=True):
        workload = self.zos.workloads.get(wid)
        if workload.info.workload_type != WorkloadType.Container:
            raise j.exceptions.Validation(f"can't expose workload {wid} of type {workload.info.workload_type}")
        ip_address = workload.network_connection[0].ipaddress
        gateways = self.fetch_myfarm_gateways()
        gateway_pool_id = self.get_gateway_pool_id()
        random.shuffle(gateways)
        for gateway in gateways:
            domain_generator = self.reserve_subdomain(
                gateway, prefix, solution_uuid, gateway_pool_id, exposed_wid=wid, ip_address=public_ip
            )
            try:
                subdomain, subdomain_id = next(domain_generator)
            except StopIteration:
                continue
            self.vdc_deployer.info(
                f"ingress proxy over custom domain: {subdomain}, name: {name}, ip_address: {ip_address}, public_ip: {public_ip}"
            )
            try:
                self._create_ingress(name, subdomain, [ip_address], port, force_https)
                return subdomain
            except Exception as e:
                self.vdc_deployer.error(f"failed to create proxy ingress config due to error {str(e)}")
                self.zos.workloads.decomission(subdomain_id)
                return

    def _create_ingress(self, name, domain, addresses, port, force_https=True):
        service_text = j.tools.jinja2.render_template(
            template_text=PROXY_SERVICE_TEMPLATE, service_name=name, port=port
        )
        self.vdc_deployer.vdc_k8s_manager.execute_native_cmd(f"echo -e '{service_text}' |  kubectl apply -f -")

        endpoint_text = j.tools.jinja2.render_template(
            template_text=PROXY_ENDPOINT_TEMPLATE, endpoint_name=name, addresses=addresses, port=port
        )
        self.vdc_deployer.vdc_k8s_manager.execute_native_cmd(f"echo -e '{endpoint_text}' |  kubectl apply -f -")

        ingress_text = j.tools.jinja2.render_template(
            template_text=PROXY_INGRESS_TEMPLATE,
            ingress_name=name,
            hostname=domain,
            service_name=name,
            service_port=port,
            force_https=force_https,
        )
        self.vdc_deployer.vdc_k8s_manager.execute_native_cmd(f"echo -e '{ingress_text}' |  kubectl apply -f -")

    def socat_proxy(self, name, src_port, dst_port, dst_ip):
        public_ip = self.vdc_instance.get_public_ip()
        if not public_ip:
            raise j.exceptions.Runtime(f"couldn't get a public ip for vdc: {self.vdc_instance.vdc_name}")
        ssh_client = self.vdc_instance.get_ssh_client(
            name,
            public_ip,
            "rancher",
            f"{self.vdc_deployer.ssh_key_path}/id_rsa" if self.vdc_deployer.ssh_key_path else None,
        )
        rc, out, _ = ssh_client.sshclient.run(f"sudo netstat -tulpn | grep :{src_port}", warn=True)
        if rc == 0:
            raise j.exceptions.Input(f"port: {src_port} is already exposed. details: {out}. choose a different port")

        socat = "/var/lib/rancher/k3s/data/current/bin/socat"
        cmd = f"{socat} tcp-listen:{src_port},reuseaddr,fork tcp:{dst_ip}:{dst_port}"
        template = f"""#!/sbin/openrc-run
        name="{name}"
        command="{cmd}"
        pidfile="/var/run/{name}.pid"
        command_background=true
        """
        template = dedent(template)
        file_name = f"socat-{name}"
        rc, out, err = ssh_client.sshclient.run(
            f"sudo touch /etc/init.d/{file_name} && sudo chmod 777 /etc/init.d/{file_name} &&  echo '{template}' >> /etc/init.d/{file_name} && sudo rc-service {file_name} start",
            warn=True,
        )
        if rc != 0:
            j.exceptions.Runtime(f"failed to expose port using socat. rc: {rc}, out: {out}, err: {err}")
        return public_ip
