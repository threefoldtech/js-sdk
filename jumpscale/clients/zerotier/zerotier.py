"""
A client that gives an interface to the zerotier api

```python
zcl = j.clients.zerotier.get("instance")

network = zcl.get_network("network_id")

#  list routes
network.routes

# add members

member = network.add_member(address, name="guest")

# Authorize member to this network
member.authorize()

```

"""


import requests
import ipaddress
from jumpscale.loader import j
from jumpscale.clients.base import Client
from jumpscale.core.base import fields


class Member:
    def __init__(self, member_data, network, address=None):
        self.raw_data = member_data
        self._address = address
        self._network = network
        self.id = member_data["id"]

    @property
    def address(self):
        if not self._address:
            self._address = self.identity.split(":")[0]
        return self._address

    @property
    def identity(self):
        return self.raw_data["config"]["identity"]

    @property
    def private_ip(self):
        return self.raw_data["config"]["ipAssignments"]

    def _update_authorization(self, authorize):
        if self.raw_data["config"]["authorized"] == authorize:
            return
        self._network.update_member(self.address, authorized=authorize)
        self.raw_data["config"]["authorized"] = authorize

    def authorize(self):
        """Authorize member to the zerotier network
        """
        self._update_authorization(True)

    def unauthorize(self):
        """Unauthorize member to the zerotier network
        """
        self._update_authorization(False)

    def __repr__(self):
        return f"Member({self.id})"


class Network:
    def __init__(self, network_data, client):
        self.id = network_data["id"]
        self._client = client
        self.raw_data = network_data

    @property
    def name(self):
        return self.raw_data["config"]["name"]

    @property
    def routes(self):
        return self.raw_data["config"]["routes"]

    def list_members(self):
        """List all members of  that network

        Returns:
            list: List of all members
        """
        return [Member(member, self) for member in self._client._send_request(f"network/{self.id}/member")]

    def add_member(self, address, name=None, private_ip=None, authorized=True):
        """Add a member to the network

        Args:
            address (str): Address of the member
            name (str, optional): Name of the member. Defaults to None.
            private_ip (str, optional): Private IP to assign. Defaults to None.
            authorized (bool, optional): Whether to authorize the user or not. Defaults to True.

        Returns:
            Member: Added member
        """
        data = {"config": {"authorized": authorized}, "name": name}
        if private_ip:
            data["config"]["ipAssignments"] = [private_ip]
        member_data = self._client._send_request(f"network/{self.id}/member/{address}", method="post", data=data)
        return Member(member_data, self, address)

    def update_member(self, address, name=None, private_ip=None, authorized=None):
        """Update a member in the network

        Args:
            address (str): Address of the member
            name (str, optional): Name of the member. Defaults to None.
            private_ip (str, optional): Private IP to assign. Defaults to None.
            authorized (bool, optional): Whether to authorize the user or not. Defaults to True.

        Returns:
            Member: Added member
        """
        return self.add_member(address, name, private_ip, authorized)

    def get_member(self, address):
        """Returns member by address

        Args:
            address (str): Member address

        Returns:
            Member: Found member
        """
        return Member(self._client._send_request(f"network/{self.id}/member/{address}"), self, address)

    def delete_member(self, address):
        """Deletes a member

        Args:
            address (str): Member address
        """
        self._client._send_request(f"network/{self.id}/member/{address}", method="delete", return_json=False)

    def __repr__(self):
        return f"Network({self.id})"


class ZerotierClient(Client):
    base_url = fields.String(default="https://my.zerotier.com/api")
    token = fields.String()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._session = None

    def _send_request(self, path, method="get", data=None, return_json=True):
        url = f"{self.base_url}/{path}"
        func_method = getattr(self.session, method)
        res = func_method(url, json=data)
        res.raise_for_status()
        if return_json:
            return res.json()
        else:
            return res.content

    @property
    def session(self):
        if not self._session:
            if not self.token:
                raise j.exceptions.Value("Please set token to use the client")
            self._session = requests.Session()
            self._session.headers["Authorization"] = f"Bearer {self.token}"
        return self._session

    def list_networks(self):
        """List networks available to user

        Returns:
            list: All available networks
        """
        return [Network(network, self) for network in self._send_request("network")]

    def get_network(self, network_id):
        """Get network by id

        Args:
            network_id (str): Network id

        Returns:
            Network: Found network
        """
        return Network(self._send_request(f"network/{network_id}"), self)

    def create_network(self, public, target_subnet=None, name=None, auto_assign=True):
        """Create a new network

        Args:
            public (bool): Specify if network is public or not
            target_subnet (str, optional): Target network to be pick assignment ips from. Defaults to None.
            name (str, optional): Name of the network. Defaults to None.
            auto_assign (bool, optional): If true auto assign addresses. Defaults to True.

        Returns:
            Network: Created network
        """
        routes = None
        config = {"private": not public, "noAutoAssignIps": not auto_assign, "routes": routes}
        if target_subnet:
            routes.append({"target": target_subnet, "via": None})
            network = ipaddress.IPv4Network(target_subnet)
            config["ipAssignmentPools"] = [{"ipRangeStart": network[0], "ipRangeEnd": network[-1]}]

        if name:
            config.update({"name": name})

        data = {"config": config}
        return Network(self._send_request(f"network", data=data, method="post"), self)

    def delete_network(self, network_id):
        """Deletes network

        Args:
            network_id (str): Network id
        """
        self._send_request(f"network/{network_id}", method="delete", return_json=False)

    def get_status(self):
        return self._send_request("status")
