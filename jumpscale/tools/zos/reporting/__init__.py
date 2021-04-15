"""This module is providing some helper to report stuff running on zos

- get_public_ip_usage example:

    ```python
    JS-NG> j.tools.zos.reporting.get_public_ip_usage()

    +========================= RESERVED IPS =========================+
    user: vdc_magidentfinal_test6       |	tid: 1751 |	wid: 7955
    user: dylanv.3bot                   |	tid: 48   |	wid: 7124
    user: vdc_hanafy_testvdc01          |	tid: 1737 |	wid: 7315
    user: vdc_ahmedthabet_demobackup    |	tid: 1763 |	wid: 8380
    +----------------------------------------------------------------+
    busy: 4     |	    free: 4         |	total:8
    +=========================     DONE     =========================+

    JS-NG> j.tools.zos.reporting.get_public_ip_usage("testnet")

    +========================= RESERVED IPS =========================+
    user: vdc_waleedhammam_thabet465    |	tid: 3214 |	wid: 515942
    user: vdc_ahmedthabet_demox1234     |	tid: 3219 |	wid: 516092
    user: vdc_magidentfinal_testoooo    |	tid: 3228 |	wid: 516807
    user: vdc_ayoubm_testayoub          |	tid: 3217 |	wid: 516013
    +----------------------------------------------------------------+
    busy: 4     |	    free: 26        |	total:30
    +=========================     DONE     =========================+

    ```

- get nodes availble capacity

    ```
    JS-NG> j.tools.zos.reporting.get_available_farm_capacity()

    Available capacity for nodes on Farm: lochristi_dev_lab in Explorer: devnet

                    Node                              CRU        MRU        SRU        HRU
    Gr8NxBLHe7yjSsnSTgTqGr7BHbyAUVPJqs8fnudEE4Sf       -3      140.0       6.25     8352.0
    qzuTJJVd5boi6Uyoco1WWnSgzTb7q8uN79AjBT9x9N3        5      152.0        0.5     8233.0
    BpTAry1Na2s1J8RAHNyDsbvaBSM3FjR4gMXEKga3UPbs        2      153.0       3.75     7903.0
    2anfZwrzskXiUHPLTqH1veJAia8G6rW2eFLy5YFMa1MP        3      150.0   19.21875     7913.0
    BBmMHCw392RLiByVEUT2ac6y6qJpbW9xj8TRdgk5rMGN        0      142.0       15.5     8243.0
    3NAkUYqm5iPRmNAnmLfjwdreqDssvsebj4uPUt9BxFPm        9      159.0      46.75     8173.0
    48YmkyvfoXnXqEojpJieMfFPnCv2enEuqEJcmhvkcdAk        3      132.0       45.0     8153.0
    ```


"""

from jumpscale.loader import j
from jumpscale.sals.zos.node_finder import NodeFinder


PUBLIC_IP_FARMS = {"devnet": "lochristi_dev_lab", "testnet": "freefarm", "mainnet": "freefarm"}
DEFAULT_EXPLORER_URLS = {
    "mainnet": "https://explorer.grid.tf/api/v1",
    "testnet": "https://explorer.testnet.grid.tf/api/v1",
    "devnet": "https://explorer.devnet.grid.tf/api/v1",
}


def get_public_ip_usage(explorer_name: str = "devnet"):
    """Provide a list of the used/free public ips

    Args:
        explorer (str, optional): explorer name should be in ["devnet", "testnet", "mainnet"]. Defaults to "devnet".

    Returns:
        str: nice view for the used ips or json
    """
    print("\n+========================= RESERVED IPS =========================+")
    explorer = j.clients.explorer.get_by_url(DEFAULT_EXPLORER_URLS[explorer_name])
    c = 0
    if not explorer_name in ["devnet", "testnet", "mainnet"]:
        raise j.exceptions.Value(f"Explorers: devnet, testnet, mainnet are only supported, you passed {explorer_name}")
    farm = explorer.farms.get(farm_name=PUBLIC_IP_FARMS[explorer_name])
    for ip in farm.ipaddresses:
        if not ip.reservation_id:
            continue
        c += 1
        workload = explorer.workloads.get(ip.reservation_id)
        owner_tid = workload.info.customer_tid
        user = explorer.users.get(owner_tid)
        print(f"user: {user.name:30}|\ttid: {owner_tid:<5}|\twid: {workload.id}")
    print("+----------------------------------------------------------------+")
    print(
        f"busy: {c:<6}|\t    free: {len(farm.ipaddresses)-c:<10}|\ttotal:{len(farm.ipaddresses):<3}"
        "\n+=========================     DONE     =========================+\n"
    )


def get_available_farm_capacity(explorer_name: str = "devnet", farm_name: str = "lochristi_dev_lab"):
    """Get nodes available capacity

    Args:
        explorer_name (str, optional):  Defaults to "devnet".
        farm_name (str, optional):  Defaults to "lochristi_dev_lab".

    Raises:
        j.exceptions.Value: In case of wrong input
    """
    explorer = j.clients.explorer.get_by_url(DEFAULT_EXPLORER_URLS[explorer_name])
    if not explorer_name in ["devnet", "testnet", "mainnet"]:
        raise j.exceptions.Value(f"Explorers: devnet, testnet, mainnet are only supported, you passed {explorer_name}")

    node_finder = NodeFinder(explorer=explorer)
    nodes = list(node_finder.nodes_search(farm_name=farm_name))

    j.tools.console.printcolors(
        f"\nAvailable capacity for nodes on Farm: {{GREEN}}{farm_name}{{RESET}} in Explorer: {{GREEN}}{explorer_name}{{RESET}}\n"
    )
    print(f'{"Node":>20} {"CRU":>32} {"MRU":>10} {"SRU":>10} {"HRU":>10}')
    for node in nodes:
        if not node_finder.filter_is_up(node):
            continue
        print(
            f"{node.node_id:>8}",
            f"{node.total_resources.cru - node.reserved_resources.cru:>8}",
            f"{node.total_resources.mru - node.reserved_resources.mru:>10}",
            f"{node.total_resources.sru - node.reserved_resources.sru:>10}",
            f"{node.total_resources.hru - node.reserved_resources.hru:>10}",
        )
    print("\n")
