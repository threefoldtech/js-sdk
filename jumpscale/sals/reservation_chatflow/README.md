# Making use of reservation_chatflow

Reservation chatflow sal functions can be called from within a chatflow to help creating,registering, and parsing the result types to be used in the chatflow.

The tool is accessible through `j.sals.reservation_chatflow`

## Available functionalities

### Validate user

`validate_user(user_info)`

### Get available nodes

Get a list of nodes from the grid that are available where a filter can be applied on them based on the farm_id, farm_name, or any of the resource capacities (cru, sru, mru, or hru).

`get_nodes(number_of_nodes, farm_id=None, farm_name, cru, sru, mru, hru)`

where :

- *number_of_nodes*:  number of nodes to be returned

- *farm_id* : (optional) used to select nodes only from a specific farm with this id

- *farm_name* : (optional) used to select nodes only from specific farm with this name

- *cru* : (optional) nodes selected should have a minumum value of cru (core resource unit) equal to this

- *sru* : (optional) nodes selected should have a minumum value of sru (ssd resource unit) equal to this

- *mru* : (optional) nodes selected should have a minumum value of mru (memory resource unit) equal to this

- *hru* : (optional) nodes selected should have a minumum value of hru (hd resource unit) equal to this

### Select a network for deployment

View all networks created by the customer_tid given and let the user select on to be used in the reservation they are about to create/register in the solution chatflow

`select_network(bot, customer_tid)`

where:

- *bot*:  the chatbot instance from the chatflow

- *customer_tid*: the 3Bot id of the customer who created the networks that the same user will be selecting from.

### Get ip range

Get an ip range by interacting with the user in the chat bot. The user can either choose to input a custom ip range or they can get a generated ip range. The bot in the chatflow is passed for the interactive questions to appear in the same chatflow.

`get_ip_range(bot)`

where :

- *bot*:  the chatbot instance from the chatflow

### Create a network reservation

Create a new network reservation. The reservation object is passed as well as the network name and other parameters needed for the creation of the network. The ip_version provided (Ipv4 or Ipv6) indicates whether the connection to the network will be using which version.

The function updates the reservation object and returns a network_config dict where the dict has the following keys `["wg","rid"]`

`create_network(network_name, reservation, ip_range, customer_tid, ip_version, expiration)`

where :

- *network_name*: The name to create the network with. Should be unique.

- *reservation*:  the reservation instance where a new network will be added to. This is the reservation that will be registered

- *ip_range*: The ip range to create the network with in the form `{IP}/16`. example: `10.35.0.0/16`

- *customer_tid*:  the 3Bot id of the user that is doing the reservation from the chatflow(the logged in user in the chatflow)

- *ip_version*:  ip version (Ipv4 or Ipv6) of the machine that will access the network later on

- *expiration*:  expiration of the network reservation

### Register any reservation

Register any reservation through the chatflow. This reservation could include anything such as a new network, container, kubernetes cluster, or zdb.  It returns the reservation id of the registered reservation

`register_reservation(reservation, expiration, customer_tid,expiration_provisioning)`

where :

- *reservation*: the reservation instance that will be registered.

- *expiration*:  expiration of the items in the reservation

- *customer_tid*:  the 3Bot id of the user that is doing the reservation from the chatflow(the logged in user in the chatflow)

- *expiration_provisioning*: expiration of the registered reservation if not processed to next state(provisioned)




### Wait for reservation to succeed or expire

Wait for reservation results to be complete, have errors, or expire. If there are errors then error message is previewed in the chatflow to the user and the chat is ended.

`wait_reservation(bot, rid)`

where:

- *bot*: the chatbot instance from the chatflow

- *rid*: the reservation id of the reservation to check for results and wait on completion, failure or expiry.

### Check for reservation failure

Interactive check if the reservation failed in the category provided, then an error message will be shown to the user in the chatflow along with the error(s) causing the failure of the reservation.

`_reservation_failed(bot, reservation)`

where :

- *bot*:  the chatbot instance from the chatflow

- *resv_id*:  the reservation to be checked for its failure

### List networks for user

List all the networks currently in DEPLOY state created by the user having the 3Bot id (tid) given

`list_network(tid, reservations)`

where :

- *tid*: 3Bot id to filter network reservations on

- *reservations*: list of reservations to look for networks in. If not provided then `j.sals.zos.get().list_reservation(tid=tid,next_action="DEPLOY")` is used to get all reservations of that user and checking in them.

### Save reservation(solutions)

After reservation registration is complete, The corresponding reservation id, solution name, and all user options selected are saved in bcdb to keep track of all solutions deplloyed by the user and their names.

`save_reservation(rid, name, url, form_info=None)`

where :

- *rid*: reservation id of the deployed reservation

- *name*: unique solution name for the deployed solution

- *url*: url of the model corresponding to the solution chatflow used.

- *form_info*: dict containing all the user selections and inputs from the chat flow.


### Get solutions

Get all solutions saved using the model corresponding to the given url.

`get_solutions(type):`

where:

- *type*: the enum represents the solution type ex: SolutionType.Network

### Cancel reservation and delete solution

Given type and solution name, the solution is deleted and the corresponding reservation based on the solution's reservation id is canceled by the explorer.

`cancel_reservation_for_solution(type, solution_name):`

where:

- *type*: the enum represents the solution type ex: SolutionType.Network

- *solution_name*: the name of the solution to be deleted and canceled

## Example

The following example includes usage of the tool in a chatflow in getting nodes, creating a network reservation, and a container reservation, then checking for its results to deploy an ubuntu container on a new network

check chatflows in js-sdk repository
