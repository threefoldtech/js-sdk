import base64
import copy
import json
import random
import time
from textwrap import dedent

import netaddr
import requests
from nacl.public import Box

from jumpscale.clients.explorer.models import DeployedReservation, NextAction
from jumpscale.clients.stellar.stellar import Network as StellarNetwork
from jumpscale.core.base import StoredFactory
from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import StopChatFlow
from jumpscale.sals.reservation_chatflow.models import SolutionType, TfgridSolution1, TfgridSolutionsPayment1

NODES_DISALLOW_PREFIX = "ZOS:NODES:DISALLOWED"
NODES_DISALLOW_EXPIRATION = 60 * 60 * 4  # 4 hours
NODES_COUNT_KEY = "ZOS:NODES:FAILURE_COUNT"


class ReservationChatflow:
    def __init__(self, **kwargs):
        """This class is responsible for managing, creating, cancelling reservations"""
        self.solutions = StoredFactory(TfgridSolution1)
        self.payments = StoredFactory(TfgridSolutionsPayment1)
        self.deployed_reservations = StoredFactory(DeployedReservation)

    @property
    def me(self):
        return j.core.identity.me

    @property
    def _explorer(self):
        return j.core.identity.me.explorer

    def list_wallets(self):
        """
        List all stellar client wallets from bcdb. Based on explorer instance only either wallets with network type TEST or STD are returned
        rtype: list
        """
        if "devnet" in self._explorer.url or "testnet" in self._explorer.url:
            network_type = StellarNetwork.TEST
        else:
            network_type = StellarNetwork.STD

        wallets_list = j.clients.stellar.list_all()
        wallets = dict()
        for wallet_name in wallets_list:
            wallet = j.clients.stellar.find(wallet_name)
            if wallet.network != network_type:
                continue
            wallets[wallet_name] = wallet
        return wallets

    def get_ip_range(self, bot):
        """prompt user to select iprange

        Args:
            bot (GedisChatBot): bot instance

        Returns:
            [IPRange]: ip selected by user
        """
        ip_range_choose = ["Configure IP range myself", "Choose IP range for me"]
        iprange_user_choice = bot.single_choice(
            "To have access to the 3Bot, the network must be configured",
            ip_range_choose,
            required=True,
            default=ip_range_choose[1],
        )
        if iprange_user_choice == "Configure IP range myself":
            ip_range = bot.string_ask("Please add private IP Range of the network")
        else:
            first_digit = random.choice([172, 10])
            if first_digit == 10:
                second_digit = random.randint(0, 255)
            else:
                second_digit = random.randint(16, 31)
            ip_range = str(first_digit) + "." + str(second_digit) + ".0.0/16"
        return ip_range

    def get_nodes(
        self,
        number_of_nodes,
        cru=None,
        sru=None,
        mru=None,
        hru=None,
        currency="TFT",
        ip_version=None,
        pool_ids=None,
        filter_blocked=True,
    ):
        """get available nodes to deploy solutions on

        Args:
            number_of_nodes (int): required nodes count
            farm_id (int, optional): id for farm to search with. Defaults to None.
            farm_names (list, optional): farms to search in. Defaults to None.
            cru (int, optional): cpu resource. Defaults to None.
            sru (int, optional): ssd resource. Defaults to None.
            mru (int, optional): memory resource. Defaults to None.
            hru (int, optional): hdd resources. Defaults to None.
            currency (str, optional): wanted currency. Defaults to "TFT".

        Raises:
            StopChatFlow: if no nodes found

        Returns:
            list of available nodes
        """

        def filter_disallowed_nodes(disallowed_node_ids, nodes):
            result = []
            for node in nodes:
                if node.node_id not in disallowed_node_ids:
                    result.append(node)
            return result

        disallowed_node_ids = []
        if filter_blocked:
            disallowed_node_ids = self.list_blocked_nodes().keys()
        if j.config.get("OVER_PROVISIONING"):
            cru = 0
            mru = 0
        nodes_distribution = self._distribute_nodes(number_of_nodes, pool_ids=pool_ids)
        # to avoid using the same node with different networks
        nodes_selected = []
        selected_ids = []
        for pool_id in nodes_distribution:
            nodes_number = nodes_distribution[pool_id]
            if not pool_ids:
                pool_id = None
            nodes = j.sals.zos.nodes_finder.nodes_by_capacity(
                cru=cru, sru=sru, mru=mru, hru=hru, currency=currency, pool_id=pool_id
            )
            nodes = filter_disallowed_nodes(disallowed_node_ids, nodes)
            nodes = self.filter_nodes(nodes, currency == "FreeTFT", ip_version=ip_version)
            for i in range(nodes_number):
                try:
                    node = random.choice(nodes)
                    while node.node_id in selected_ids:
                        node = random.choice(nodes)
                except IndexError:
                    raise StopChatFlow(
                        "Failed to find resources for this reservation. If you are using a low resources environment like testnet, please make sure to allow over provisioning from the settings tab in dashboard. For more info visit <a href='https://manual2.threefold.io/#/3bot_settings?id=developers-options'>our manual</a>",
                        htmlAlert=True,
                    )
                nodes.remove(node)
                nodes_selected.append(node)
                selected_ids.append(node.node_id)
        return nodes_selected

    def filter_nodes(self, nodes, free_to_use, ip_version=None):
        """filter nodes by free to use flag

        Args:
            nodes (list of nodes objects)
            free_to_use (bool)

        Returns:
            list of filtered nodes
        """
        nodes = filter(j.sals.zos.nodes_finder.filter_is_up, nodes)
        nodes = list(nodes)
        if free_to_use:
            nodes = list(nodes)
            nodes = filter(j.sals.zos.nodes_finder.filter_is_free_to_use, nodes)
        elif not free_to_use:
            nodes = list(nodes)

        if ip_version:
            use_ipv4 = ip_version == "IPv4"

            if use_ipv4:
                nodefilter = j.sals.zos.nodes_finder.filter_public_ip4
            else:
                nodefilter = j.sals.zos.nodes_finder.filter_public_ip6

            nodes = filter(j.sals.zos.nodes_finder.filter_is_up, filter(nodefilter, nodes))
            if not nodes:
                raise StopChatFlow("Could not find available access node")
        return list(nodes)

    def _distribute_nodes(self, number_of_nodes, pool_ids):
        nodes_distribution = {}
        nodes_left = number_of_nodes
        result_ids = list(pool_ids) if pool_ids else []
        if not pool_ids:
            pools = self._explorer.pools.list()
            result_ids = []
            for p in pools:
                result_ids.append(p.pool_id)
        random.shuffle(result_ids)
        id_pointer = 0
        while nodes_left:
            pool_id = result_ids[id_pointer]
            if pool_id not in nodes_distribution:
                nodes_distribution[pool_id] = 0
            nodes_distribution[pool_id] += 1
            nodes_left -= 1
            id_pointer += 1
            if id_pointer == len(result_ids):
                id_pointer = 0
        return nodes_distribution

    def validate_user(self, user_info):
        """validate user information data to authentication

        Args:
            user_info (dict): user information
        """
        if not j.core.config.get_config().get("threebot_connect", True):
            error_msg = """
            This chatflow is not supported when 3Bot is in dev mode.
            To enable 3Bot connect : `j.core.config.set('threebot_connect', True)`
            """
            raise j.exceptions.Runtime(error_msg)
        if not user_info["email"]:
            raise j.exceptions.Value("Email shouldn't be empty")
        if not user_info["username"]:
            raise j.exceptions.Value("Name of logged in user shouldn't be empty")
        return self._explorer.users.get(name=user_info["username"], email=user_info["email"])

    def block_node(self, node_id):
        count = j.core.db.hincrby(NODES_COUNT_KEY, node_id)
        expiration = count * NODES_DISALLOW_EXPIRATION
        node_key = f"{NODES_DISALLOW_PREFIX}:{node_id}"
        j.core.db.set(node_key, expiration, ex=expiration)

    def unblock_node(self, node_id, reset=True):
        node_key = f"{NODES_DISALLOW_PREFIX}:{node_id}"
        j.core.db.delete(node_key)
        if reset:
            j.core.db.hdel(NODES_COUNT_KEY, node_id)

    def list_blocked_nodes(self):
        """
        each blocked node is stored in a key with a prefix ZOS:NODES:DISALLOWED:{node_id} and its value is the expiration period for it.
        number of failure count is defined in hash with key ZOS:NODES:FAILURE_COUNT. the hash keys are node_ids and values are count of how many times the node has been blocked

        returns
            dict: {node_id: {expiration: .., failure_count: ...}}
        """
        blocked_node_keys = j.core.db.keys(f"{NODES_DISALLOW_PREFIX}:*")
        failure_count_dict = j.core.db.hgetall(NODES_COUNT_KEY)
        blocked_node_values = j.core.db.mget(blocked_node_keys)
        result = {}
        for idx, key in enumerate(blocked_node_keys):
            key = key[len(NODES_DISALLOW_PREFIX) + 1 :]
            node_id = key.decode()
            expiration = int(blocked_node_values[idx])
            failure_count = int(failure_count_dict[key])
            result[node_id] = {"expiration": expiration, "failure_count": failure_count}
        return result

    def clear_blocked_nodes(self):
        blocked_node_keys = j.core.db.keys(f"{NODES_DISALLOW_PREFIX}:*")
        if blocked_node_keys:
            j.core.db.delete(*blocked_node_keys)
        j.core.db.delete(NODES_COUNT_KEY)


reservation_chatflow = ReservationChatflow()
