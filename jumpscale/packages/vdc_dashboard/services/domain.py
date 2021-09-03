from jumpscale.tools.servicemanager.servicemanager import BackgroundService
from jumpscale.clients.explorer.models import NextAction, WorkloadType
from jumpscale.loader import j
from jumpscale.sals.vdc.models import KubernetesRole


class VDCDomainsValidation(BackgroundService):
    def __init__(self, interval=60 * 5, *args, **kwargs):
        super().__init__(interval, *args, **kwargs)

    def job(self):
        # redeploy subdomain
        if not j.sals.vdc.list_all():
            raise j.exceptions.Value(
                "Couldn't find any vdcs on this machine, Please make sure to have it configured properly"
            )
        vdc = j.sals.vdc.get(list(j.sals.vdc.list_all())[0])
        vdc.load_info()
        domains = set()
        try:
            from jumpscale.packages.vdc_dashboard.sals.vdc_dashboard_sals import get_all_vdc_deployments

            deployments = get_all_vdc_deployments(vdc.vdc_name)
            for deployment in deployments:
                j.logger.info(f"restoring domain for deployment: {deployment}")
                domain_name = deployment.get("Domain")
                if not domain_name:
                    continue
                if domain_name in domains:
                    continue
                domains.add(domain_name)
        except Exception as e:
            j.logger.error(f"failed to fetch all deployed domains due to error {str(e)}")

        self.validate_solution_domains(vdc, domains)

    def validate_solution_domains(self, vdc, domains):
        # get all deployed domains
        # make sure they point to ip_address otherwise decomission it
        public_ip = [n for n in vdc.kubernetes if n.role == KubernetesRole.MASTER][-1].public_ip
        deployed_domains = set()
        zos = j.sals.zos.get()
        # get the deployed domains that exist in the solution domains
        for workload in zos.workloads.list_workloads(j.core.identity.me.tid, NextAction.DEPLOY):
            if workload.info.workload_type != WorkloadType.Subdomain:
                continue
            if workload.domain not in domains:
                continue
            if public_ip in workload.ips:
                j.logger.info(f"domain: {workload.domain} is satisfied by workload: {workload.id}")
                deployed_domains.add(workload.domain)
            else:
                j.logger.warning(
                    f"domain: {workload.domain} is deployed in workload: {workload.id} but pointing to invalid ips: {workload.ips}"
                )
                zos.workloads.decomission(workload.id)
        # loop over solution domains and redeploy the missing ones
        gateways = zos.gateways_finder.gateways_search()
        domain_mapping = {}
        wids = []
        for gw in gateways:
            if not gw.managed_domains:
                continue
            domain_mapping.update({dom: gw for dom in gw.managed_domains})
        all_pools = zos.pools.list()
        node_mapping = {}
        for pool in all_pools:
            node_mapping.update({node_id: pool.pool_id for node_id in pool.node_ids})
        for domain_name in domains:
            if domain_name in deployed_domains:
                continue
            j.logger.info(f"domain {domain_name} is missing")
            try:
                parent_domain = ".".join(domain_name.split(".")[1:])
                gw = domain_mapping.get(parent_domain)
                if not gw:
                    j.logger.warning(f"unable to get the gateway that managed this domain {domain_name}")
                    continue
                pool_id = node_mapping.get(gw.node_id)
                if not pool_id:
                    farm_name = zos._explorer.farms.get(gw.farm_id).name
                    pool = zos.pools.create(0, 0, 0, farm_name)
                    pool = zos.pools.get(pool.reservation_id)
                    node_mapping.update({node_id: pool.pool_id for node_id in pool.node_ids})
                    pool_id = pool.pool_id
                domain = zos.gateway.sub_domain(gw.node_id, domain_name, [public_ip], pool_id)
                wids.append(zos.workloads.deploy(domain))
            except Exception as e:
                j.logger.critical(f"failed to redeploy domain {domain_name} due to error {str(e)}")
        for wid in wids:
            workload = zos.workloads.get(wid)
            try:
                j.logger.info(f"waiting workload: {wid}")
                success = zos.workloads.wait(wid, 1)
                if not success:
                    j.logger.critical(f"subdomain: {workload.domain} of wid: {wid} failed to redeploy")
                else:
                    j.logger.info(f"subdomain: {workload.domain} of wid: {wid} successfully deployed")
            except Exception as e:
                j.logger.critical(
                    f"subdomain: {workload.domain} of wid: {wid} failed to redeploy due to error {str(e)}"
                )


service = VDCDomainsValidation()
