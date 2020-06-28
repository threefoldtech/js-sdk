from jumpscale.loader import j

from ipaddress import IPv4Address, IPv6Address

# TODO: fixme when ipaddr is primitive in types.
def addr_check(addr):
    try:
        IPv4Address(addr)
    except:
        try:
            IPv6Address(addr)
        except:
            return False
        else:
            return True
    else:
        return True

"""
j.tools.tf_gateway.tcpservice_register("bing", "www.bing.com", "122.124.214.21")
j.tools.tf_gateway.domain_register_a("ahmed", "bots.grid.tf.", "123.3.23.54")

"""

def local_redis():
    local = None
    try:
        local = j.clients.redis.get('local')
    except:
        local = j.clients.redis.new('local')

    return local

def tcpservice_register(service_name, domain, service_endpoint):
    """
    register a tcpservice to be used by tcprouter in local_redis()

    :param service_name: service name to register in tcprouter
    :type service_name: str
    :param domain: (Server Name Indicator SNI) (e.g www.facebook.com)
    :type domain: str
    :param service_endpoint: TLS endpoint 102.142.96.34:443 "ip:port"
    :type service_endpoint: string
    """
    service = {}
    service["Key"] = "/tcprouter/service/{}".format(service_name)
    record = {"addr": service_endpoint, "sni": domain, "name": service_name}
    json_dumped_record_bytes = j.data.serializers.json.dumps(record).encode()
    b64_record = j.data.serializers.base64.encode(json_dumped_record_bytes).decode()
    service["Value"] = b64_record
    local_redis().set(service["Key"], j.data.serializers.json.dumps(service))

def domain_register(threebot_name, bots_domain="bots.grid.tf.", record_type="a", records=None):
    """registers domain in coredns (needs to be authoritative)

    e.g: ahmed.bots.grid.tf

    requires nameserver on bots.grid.tf (authoritative)
    - ahmed is threebot_name
    - bots_domain is bots.grid.tf

    :param threebot_name: threebot_name
    :type threebot_name: str
    :param bots_domain: str, defaults to "bots.grid.tf."
    :type bots_domain: str, optional
    :param record_type: valid dns record (a, aaaa, txt, srv..), defaults to "a"
    :type record_type: str, optional
    :param records: records list, defaults to None
    :type records: [type], optional is [ {"ip":machine ip}] in case of a/aaaa records
    """
    if not bots_domain.endswith("."):
        bots_domain += "."
    data = {}
    records = records or []
    if local_redis().hexists(bots_domain, threebot_name):
        data = j.data.serializers.json.loads(local_redis().hget(bots_domain, threebot_name))

    if record_type in data:
        records.extend(data[record_type])
    data[record_type] = records
    local_redis().hset(bots_domain, threebot_name, j.data.serializers.json.dumps(data))

def domain_register_a(name, domain, record_ip):
    """registers A domain in coredns (needs to be authoritative)

    e.g: ahmed.bots.grid.tf

    requires nameserver on bots.grid.tf (authoritative)
    - ahmed is threebot_name
    - bots_domain is bots.grid.tf

    :param threebot_name: myhost
    :type threebot_name: str
    :param bots_domain: str, defaults to "grid.tf."
    :type bots_domain: str, optional
    :param record_ip: machine ip in ipv4 format
    :type record_ip: str
    """
    if addr_check(record_ip):
        return domain_register(name, domain, record_type="a", records=[{"ip": record_ip}])
    else:
        raise j.exceptions.Value("invalid ip {record_ip}".format(**locals()))

def domain_register_aaaa(threebot_name, bots_domain, record_ip):
    """registers A domain in coredns (needs to be authoritative)

    e.g: ahmed.bots.grid.tf

    requires nameserver on bots.grid.tf (authoritative)
    - ahmed is threebot_name
    - bots_domain is bots.grid.tf

    :param threebot_name: threebot_name
    :type threebot_name: str
    :param bots_domain: str, defaults to "bots.grid.tf."
    :type bots_domain: str, optional
    :param record_ip: machine ip in ipv6 format
    :type record_ip: str
    """
    if addr_check(record_ip):
        return domain_register(threebot_name, bots_domain, record_type="aaaa", records=[{"ip": record_ip}])
    else:
        raise j.exceptions.Value("invalid ip {record_ip}".format(**locals()))


def test():
    domain_register_a("ns", "3bot.me", "134.209.90.92")
    domain_register_a("a", "3bot.me", "134.209.90.92")
