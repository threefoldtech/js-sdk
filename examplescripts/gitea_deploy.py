import math
import random, time
import datetime
import netaddr
from jumpscale.god import j
from jumpscale.sals.reservation_chatflow.models import TfgridSolution1, TfgridSolutionsPayment1, SolutionType
from jumpscale.sals.reservation_chatflow.reservation_chatflow import Network


def wait_payment(self, rid, reservation_create_resp=None):
    """wait slide untill payment is ready
        Args:
            rid (int): customer tid
            threebot_app (bool, optional): is using threebot app payment. Defaults to False.
            reservation_create_resp (jumpscale.clients.explorer.models.TfgridWorkloadsReservation1, optional): reservation object response. Defaults to None.
        """

    # wait to check payment is actually done next_action changed from:PAY
    def is_expired(reservation):
        return reservation.data_reservation.expiration_provisioning.timestamp() < j.data.time.get().timestamp

    reservation = self._explorer.reservations.get(rid)
    while True:
        remaning_time = j.data.time.get(reservation.data_reservation.expiration_provisioning).humanize(
            granularity=["minute", "second"]
        )
        deploying_message = f"""
Payment being processed...\n
Deployment will be cancelled if payment is not successful {remaning_time}
"""
        print(deploying_message)
        if reservation.next_action != "PAY":
            return
        if is_expired(reservation):
            res = f"# Failed to wait for payment for reservation:```{reservation.id}```:\n"
            for x in reservation.results:
                if x.state == "ERROR":
                    res += f"\n### {x.category}: ```{x.message}```\n"
            link = f"{self._explorer.url}/reservations/{reservation.id}"
            res += f"<h2> <a href={link}>Full reservation info</a></h2>"
            j.sals.zos.reservation_cancel(rid)
            break
        time.sleep(5)
        reservation = self._explorer.reservations.get(rid)


def _check_payment(self, resv_id, currency, total_amount, timeout=300):
    """Returns True if user has paied alaready, False if not
        """
    now = datetime.datetime.now()
    effects_sum = 0
    while now + datetime.timedelta(seconds=timeout) > datetime.datetime.now():
        transactions = self.wallet.list_transactions()
        for transaction in transactions:
            if transaction.memo_text == f"{resv_id}":
                effects = self.wallet.get_transaction_effects(transaction.hash)
                for e in effects:
                    if e.asset_code == currency:
                        effects_sum += e.amount
        if effects_sum >= total_amount:
            return True
    return False


def get_ip_range():
    first_digit = random.choice([172, 10])
    if first_digit == 10:
        second_digit = random.randint(0, 255)
    else:
        second_digit = random.randint(16, 31)
    return str(first_digit) + "." + str(second_digit) + ".0.0/16"


class Network_child(Network):

    def update(self, tid, currency=None, client=None):
        """create reservations and update status and show payments stuff
        Args:
            tid (int): customer tid (j.core.identity.me.tid)
            currency (str, optional): "TFT" or "FreeTFT". Defaults to None.

        Returns:
            bool: True if successful
        """
        if self._is_dirty:
            reservation = j.sals.zos.reservation_create()
            reservation.data_reservation.networks.append(self._network)
            form_info = {
                "chatflow": "network",
                "Currency": self.currency,
                "Solution expiration": self._expiration,
            }
            metadata = j.sals.reservation_chatflow.get_solution_metadata(
                self.name, SolutionType.Network, form_info=form_info
            )

            metadata["parent_network"] = self.resv_id
            self._sal.add_reservation_metadata(reservation, metadata)

            reservation_create = self._sal.register_reservation(
                reservation, self._expiration, tid, currency=currency
            )
            rid = reservation_create.reservation_id

            # payout farmer
            j.sals.zos.billing.payout_farmers(client, reservation_create)
        return True

    def ask_ip_from_node(self, node):
        """ask for free ip from a specific node and mark it as used in chatbot

        Args:
            node (jumpscale.client.explorer.models.TfgridDirectoryNode2): reqired node to ask ip from
            message (str): message to the chatflow slide

        Returns:
            [str]: free ip
        """
        ip_range = self.get_node_range(node)
        hosts = netaddr.IPNetwork(ip_range).iter_hosts()
        next(hosts)  # skip ip used by node
        for host in hosts:
            ip = str(host)
            if ip not in self._used_ips:
                ip_address = ip
                break
        self._used_ips.append(ip_address)
        return ip_address

    def get_free_ip(self, node):
        """return free ip

        Args:
            node (jumpscale.client.explorer.models.TfgridDirectoryNode2): reqired node to get free ip from

        Returns:
            [str]: free ip to use
        """
        ip_range = self.get_node_range(node)
        hosts = netaddr.IPNetwork(ip_range).iter_hosts()
        next(hosts)  # skip ip used by node
        for host in hosts:
            ip = str(host)
            if ip not in self._used_ips:
                return ip
        return None


class GiteaDeploy:
    """
    gitea container deploy
    """

    user_form_data = dict()
    HUB_URL = "https://hub.grid.tf/tf-official-apps/gitea-latest.flist"
    user_form_data["chatflow"] = "gitea"

    user_form_data = {}
    user_form_data["chatflow"] = "network"
    network_name = "Network_name"
    user_form_data["Currency"] = "FreeTFT"
    expiration = j.data.time.get().timestamp + 9900
    ipversion = "IPV4"

    access_node = j.sals.reservation_chatflow.get_nodes(1, currency=user_form_data["Currency"], ip_version=ipversion)[0]
    print("Get access node")

    reservation = j.sals.zos.reservation_create()
    print("Intialize network reservation")
    ip_range = get_ip_range()
    print("Get IpRange")
    res = j.sals.reservation_chatflow.get_solution_metadata(network_name, SolutionType.Network, user_form_data)
    reservation = j.sals.reservation_chatflow.add_reservation_metadata(reservation, res)

    config = j.sals.reservation_chatflow.create_network(
        network_name,
        reservation,
        ip_range,
        j.core.identity.bola_main.tid,
        ipversion,
        access_node,
        expiration=expiration,
        currency=user_form_data["Currency"],
    )

    #change wallet name for one used and make sure have TFT or FreeTFT
    client = j.clients.stellar.get(name="my_wallet", network="TEST")
    client.activate_through_friendbot()
    client.add_known_trustline("TFT")
    # if you don't have a trustline to the issuer of TFT on stellar
    client.add_known_trustline("FreeTFT")
    # payout farmer
    j.sals.zos.billing.payout_farmers(client, config["reservation_create"])

    print("Wireguard configuration")
    print(config["wg"])
    print("Copy and up your wireguard")

    network = Network_child(
        reservation.data_reservation.networks[0],
        expiration,
        None,
        [reservation],
        user_form_data["Currency"],
        config["rid"],
    )
    currency = network.currency

    user_form_data["Solution name"] = "gitea_solution_script"

    user_form_data["Public key"] = "Puplic_key".split("\n")[0]

    #add your expiration time
    expiration = j.data.time.get().timestamp + 9900
    user_form_data["Solution expiration"] = j.data.time.get(expiration).humanize()

    #configuration of oddo and postgres
    database_name = "postgres"
    database_user = "postgres"
    database_password = "postgres"
    repository_name = "myrepo"

    user_form_data["Database Name"] = database_name
    user_form_data["Database User"] = database_user
    user_form_data["Database Password"] = database_password
    user_form_data["Repository"] = repository_name

    query = {"mru": math.ceil(1024 / 1024), "cru": 2, "sru": 6}
    # create new reservation
    reservation = j.sals.zos.reservation_create()

    query["currency"] = currency

    node_selected = j.sals.reservation_chatflow.get_nodes(1, **query)[0]
    network.add_node(node_selected)
    ip_address = network.ask_ip_from_node(node_selected)
    user_form_data["IP Address"] = ip_address

    var_dict = {
        "pub_key": user_form_data["Public key"],
        "POSTGRES_DB": user_form_data["Database Name"],
        "DB_TYPE": "postgres",
        "DB_HOST": f"{ip_address}:5432",
        "POSTGRES_USER": user_form_data["Database User"],
        "APP_NAME": user_form_data["Repository"],
        "ROOT_URL": f"http://{ip_address}:3000",
    }
    database_password_encrypted = j.sals.zos.container.encrypt_secret(
        node_selected.node_id, user_form_data["Database Password"]
    )
    secret_env = {"POSTGRES_PASSWORD": database_password_encrypted}
    network.update(j.core.identity.me.tid, currency=currency, client=client)
    storage_url = "zdb://hub.grid.tf:9900"
    entry_point = "/start_gitea.sh"

    # create container
    cont = j.sals.zos.container.create(
        reservation=reservation,
        node_id=node_selected.node_id,
        network_name=network.name,
        ip_address=ip_address,
        flist=HUB_URL,
        storage_url=storage_url,
        env=var_dict,
        interactive=False,
        entrypoint=entry_point,
        cpu=2,
        public_ipv6=True,
        memory=1024,
        secret_env=secret_env,
    )

    metadata = dict()
    metadata["chatflow"] = user_form_data["chatflow"]
    metadata["Solution name"] = user_form_data["Solution name"]
    metadata["Solution expiration"] = user_form_data["Solution expiration"]
    metadata["Database name"] = user_form_data["Database Name"]
    metadata["Database user"] = user_form_data["Database User"]
    metadata["Database password"] = user_form_data["Database Password"]
    metadata["Repository"] = user_form_data["Repository"]

    res = j.sals.reservation_chatflow.get_solution_metadata(
        user_form_data["Solution name"], SolutionType.Gitea, metadata
    )
    print("Create gitea reservation")
    reservation = j.sals.reservation_chatflow.add_reservation_metadata(reservation, res)

    reservation = j.sals.reservation_chatflow.register_reservation(
        reservation, expiration, customer_tid=j.core.identity.me.tid, currency=currency
    )
    print(f"Register gitea reservation with id {reservation.reservation_id}")
    print(f"payout farmer")
    j.sals.zos.billing.payout_farmers(client, reservation)
    print(f"payout farmer")
    j.sals.reservation_chatflow.save_reservation(
        reservation.reservation_id, user_form_data["Solution name"], SolutionType.Gitea, user_form_data
    )

    res = f"""\
# gitea has been deployed successfully: your reservation id is: {reservation.reservation_id}
To connect ```ssh git@{ip_address}``` .It may take a few minutes.
open gitea from browser at ```{ip_address}:3000```
            """

    print(res)


GiteaDeploy
