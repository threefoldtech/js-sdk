"""
Helper to get nameservers information and resolving domains.

"""

import dns
import dns.message
import dns.rdataclass
import dns.rdatatype
import dns.query
import dns.resolver


class DNSClient:
    def __init__(self, nameservers=None, port=53):
        self.nameservers = nameservers or ["8.8.8.8", "8.8.4.4"]
        if "localhost" in self.nameservers:
            nameservers.pop(nameservers.index("localhost"))
            nameservers.append("127.0.0.1")
        self.resolver = dns.resolver.Resolver(configure=False)
        self.resolver.nameservers = self.nameservers
        self.resolver.port = port

    def get_nameservers(self, domain="threefoldtoken.org"):
        answer = self.resolver.query(domain, "NS")

        res = []
        for rr in answer:
            res.append(rr.target.to_text())
        return res

    def get_namerecords(self, url="www.threefoldtoken.org"):
        """
        return ip addr for a full name
        """
        answer = self.resolver.query(url, "A")

        res = []
        for rr in answer:
            res.append(rr.address)
        return res

    def is_free(self, domain, domain_type="A"):
        try:
            self.query(domain, domain_type)
        except:
            return True
        return False

    def query(self, *args, **kwargs):
        return self.resolver.query(*args, **kwargs)


def export_module_as():
    return DNSClient()
