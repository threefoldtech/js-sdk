import os
from jumpscale.loader import j


class NameManager:
    def __init__(self, domain_type="namecom", pool_id=None, gateway=None, proxy_instance=None, exposed_wid=None):
        self.domain_type = domain_type
        self.gateway = gateway
        self.proxy_instance = proxy_instance
        self.pool_id = pool_id

    def create_subdomain(self, parent_domain=None, prefix=None, ip_addresses=None, vdc_uuid=None):
        if self.domain_type == "namecom":
            nc = j.clients.name.get("VDC")
            nc.username = os.environ.get("VDC_NAME_USER")
            nc.token = os.environ.get("VDC_NAME_TOKEN")
            existing_records = nc.nameclient.list_records_for_host(parent_domain, prefix)
            if existing_records:
                for record_dict in existing_records:
                    nc.nameclient.delete_record(record_dict["fqdn"][:-1], record_dict["id"])

            for address in ip_addresses:
                nc.nameclient.create_record(parent_domain, prefix, "A", address)
            return f"{prefix}.{parent_domain}", None
        else:
            prefix = j.data.text.removesuffix(prefix, ".vdc")
            domain_generator = self.proxy_instance.reserve_subdomain(
                self.gateway, prefix, vdc_uuid, pool_id=self.pool_id, ip_address=ip_addresses[0]
            )
            subdomain, subdomain_id = next(domain_generator)
            return subdomain, subdomain_id
