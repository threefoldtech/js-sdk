"""
Helper to get nameservers information and resolving domains.

"""
# TODO: update code


try:
    import dns
    import dns.message
    import dns.rdataclass
    import dns.rdatatype
    import dns.query
    import dns.resolver

except ImportError as e:
    print("WARNING install dnspython: 'pip3 install dnspython'")


class DNSClient:
    def __init__(self, nameservers=None, port=53):
        self.nameservers = nameservers or ["8.8.8.8", "8.8.4.4"]
        if "localhost" in self.nameservers:
            nameservers.pop(nameservers.index("localhost"))
            nameservers.append("127.0.0.1")
        self.resolver = dns.resolver.Resolver(configure=False)
        self.resolver.nameservers = self.nameservers
        self.resolver.port = port

    def nameservers_get(self, domain="threefoldtoken.org"):
        answer = self.resolver.query(domain, "NS")

        res = []
        for rr in answer:
            res.append(rr.target.to_text())
        return res

    def namerecords_get(self, url="www.threefoldtoken.org"):
        """
        return ip addr for a full name
        """
        answer = self.resolver.query(url, "A")

        res = []
        for rr in answer:
            res.append(rr.address)
        return res


resolver = DNSClient()
