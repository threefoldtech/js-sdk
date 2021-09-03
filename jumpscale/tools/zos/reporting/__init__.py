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
    JS-NG> j.tools.zos.reporting.get_available_farm_capacity(explorer_name="testnet", farm_name="freefarm")

    Available capacity for nodes on Farm: freefarm in Explorer: testnet

    +----------------------------------------------+-----+-------+--------+--------+
    | Node                                         | CRU | MRU   | SRU    | HRU    |
    +----------------------------------------------+-----+-------+--------+--------+
    | 26ZATmd3K1fjeQKQsi8Dr7bm9iSRa3ePsV8ubMcbZEuY | 1   | 0.0   | 141.0  | 913.0  |
    | 8zPYak76CXcoZxRoJBjdU69kVjo7XYU1SFE2NEK4UMqn | -1  | 0.0   | 243.0  | 0.0    |
    | 85J3zEvcqDoPaN7qQHRQ2QgPVcYdCvp8JmRY5qAwzxfm | -1  | 2.0   | 278.0  | 883.0  |
    | FED1ZsfbUz3jcJzzqJWyGaoGC61bdN8coKJNte96Fo7k | -2  | 0.0   | 265.75 | 0.0    |
    | DJoL9ZV53K5YQurmxor2BLWTPf3WA9dT3RsFWeDeAx1z | 0   | 0.0   | 212.0  | 1103.0 |
    | Hx4B6B8s8yQ5ABLStma1kZ33kCuprSxzU8tY4totKbWH | -1  | 0.0   | 246.0  | 0.0    |
    | 8YLrviP78Msue8ptejusq7xxxAgD4ZHNDXXF9KXVGYWr | 4   | 7.0   | 299.0  | 0.0    |
    | APxTCEYX2YjF9dgDGwRrGsi6gNmQ1a1rzgXaHrAAdbST | -7  | 133.0 | 6.0    | 7563.0 |
    | 52phivuJMFXcuLwGP7rkbjVRaxjTDnP9japDwf8fBAtn | 24  | 187.0 | 476.0  | 8263.0 |
    | 89HWyx6iurJKk7BXEa4tL7ziWFHwycRwidMtPWsepgZo | 19  | 182.0 | 450.0  | 8283.0 |
    | 3VBKrSTVieFzJ9Bv9MSzvQBQcTwnxgPhC9tMNsUsv5BH | 13  | 165.0 | 76.0   | 8363.0 |
    | DHjz97zzNY1BxpVZ1mmv3gwwmPRN9oB91pSjeRVDZe6A | 3   | 145.0 | 1.0    | 8283.0 |
    | EMg1z3up8UcYNK5Rbfya7kKkKsuyqhNWrv15JKHERbuW | 9   | 142.0 | 100.0  | 8313.0 |
    | 3xhQQssbgsUxJtsGoDmnF77SyogsC71Q8UFMkAAUi3ki | 14  | 167.0 | 226.0  | 8383.0 |
    | 3pRRo2s6h1XPSiNY5W98nPUUmWYN5NzrvyUCkpFugfL7 | 8   | 155.0 | 26.0   | 7923.0 |
    | HC1WPUg8GMsbcYakHbHZxeWB1dGhwyvdjGr59dfk7vwE | 10  | 161.0 | 122.0  | 8373.0 |
    | FzWp4mhvC6xutRebE8JRv9bMjquioQbdBJoSXgNxtzSG | 20  | 179.0 | 375.0  | 8373.0 |
    | 7e8iFD2inToLQzqTp855SpYf8LfVt9K3MUzrTWoqtvov | -3  | 143.0 | 31.0   | 8153.0 |
    | BhAgw6PMUUETKQmZCCGqfNF2Pt4n6FKW4D8p7yY7hWpQ | 7   | 154.0 | 46.75  | 8373.0 |
    | 2imakaznKfYx3vA4CDcTKxWbw9GcW3eXX8wQfr61X1Lz | 8   | 139.0 | 75.0   | 8353.0 |
    | 93qJrfeBqYiuVC973n9kPX79uA4rZU6oHL9pdJGBegHL | 1   | 130.0 | 16.0   | 8363.0 |
    | 3otHJ8H3Wv5oSCWQWqharzYmB5BdWecMhUB11D88YZwC | 20  | 179.0 | 325.0  | 8373.0 |
    | 9Bkf6fmWkAh4kMgawjpP8N35Ybh1AhzaRHisBawR8ef3 | 24  | 187.0 | 376.0  | 8363.0 |
    +----------------------------------------------+-----+-------+--------+--------+



"""

from jumpscale.loader import j
from jumpscale.sals.zos.node_finder import NodeFinder


DEFAULT_EXPLORER_URLS = {
    "mainnet": "https://explorer.grid.tf/api/v1",
    "testnet": "https://explorer.testnet.grid.tf/api/v1",
    "devnet": "https://explorer.devnet.grid.tf/api/v1",
}


def get_public_ip_usage(explorer_name: str = "devnet", farms_names=None):
    """Provide a list of the used/free public ips

    Args:
        explorer (str, optional): explorer name should be in ["devnet", "testnet", "mainnet"]. Defaults to "devnet".
        farms_name (list, optional): farm name / list of farms names to search in, None will get all values
    Returns:
        str: nice view for the used ips or json
    """
    print("\nGetting public ip usage ...")
    explorer = j.clients.explorer.get_by_url(DEFAULT_EXPLORER_URLS[explorer_name])

    if not explorer_name in ["devnet", "testnet", "mainnet"]:
        raise j.exceptions.Value(f"Explorers: devnet, testnet, mainnet are only supported, you passed {explorer_name}")

    farms_with_public_ip = []
    if farms_names:

        if not isinstance(farms_names, list):
            farms_names = [farms_names]

        for farm_name in farms_names:
            try:
                farm = explorer.farms.get(farm_name=farm_name)
                farms_with_public_ip.append(farm)
            except Exception as e:
                j.logger.error(f"No farm with the name {farm_name} exists in explorer {explorer_name} due to {str(e)}")

    farms = farms_with_public_ip or [farm for farm in explorer.farms.list() if farm.ipaddresses]

    for farm in farms:
        c = 0
        ip_usage = [["Username", "Owner tid", "WID"]]
        for ip in farm.ipaddresses:
            if not ip.reservation_id:
                continue
            c += 1
            workload = explorer.workloads.get(ip.reservation_id)
            owner_tid = workload.info.customer_tid
            user = explorer.users.get(owner_tid)
            ip_usage.append([user.name, owner_tid, workload.id])
        ip_usage.append(["---------------------------------------------------------------", "--------", "--------"])
        ip_usage.append([f"Busy: {c}", f"Free: {len(farm.ipaddresses) - c}", f"Total: {len(farm.ipaddresses)}"])
        j.data.terminaltable.print_table(
            j.tools.console.printcolors(
                f"\nReserved public IPs on Farm: {{GREEN}}{farm.name}{{RESET}} in Explorer: {{GREEN}}{explorer_name}{{RESET}}\n"
            ),
            ip_usage,
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

    capacity = [["Node", "CRU", "MRU", "SRU", "HRU"]]
    for node in nodes:
        if not node_finder.filter_is_up(node):
            continue
        capacity.append(
            [
                node.node_id,
                node.total_resources.cru - node.reserved_resources.cru,
                node.total_resources.mru - node.reserved_resources.mru,
                node.total_resources.sru - node.reserved_resources.sru,
                node.total_resources.hru - node.reserved_resources.hru,
            ]
        )
    j.data.terminaltable.print_table(
        j.tools.console.printcolors(
            f"\nAvailable capacity for nodes on Farm: {{GREEN}}{farm_name}{{RESET}} in Explorer: {{GREEN}}{explorer_name}{{RESET}}\n"
        ),
        capacity,
    )
