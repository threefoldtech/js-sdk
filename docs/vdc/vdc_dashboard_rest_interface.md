## VDC Dashboard API

When deploying a new VDC, some endpoints will be available to deal with the vdc along with the UI dashboard.

*note*: All endpoints are protected by checking for `password` param passed in the JSON body of the POST request and compared to the vdc password used during the vdc creation.

The functionalities can be accessed through the following endpoints:


## Get all VDC info

- `<YOUR_VDC_DOMAIN>/api/controller/vdc`
- method: POST
- Body params:
    - *password*: (string) password to access vdc
- Return:
    - *vdc*: (JSON string) all vdc information


## Get all worker nodes

- `<YOUR_VDC_DOMAIN>/api/controller/node/list`
- method: POST
- Body params:
    - *password*: (string) password to access vdc
- Return:
    - *kubernetes*: (JSON string) all kubernetes worker nodes information

## Add new worker node

- `<YOUR_VDC_DOMAIN>/api/controller/node/add`
- method: POST
- Body params:
    - *password*: (string) password to access vdc
    - *flavor*: (string) flavor(specs) of the new node to be added e.g: SMALL
- Return:
    - *wids*: (JSON string) list of workload ids of the new node/s added


## Delete existing worker node
- `<YOUR_VDC_DOMAIN>/api/controller/node/delete`
- method: POST
- Body params:
    - *password*: (string) password to access vdc
    - *wid*: (string) workload id of the node to be deleted


## Get all storage containers

- `<YOUR_VDC_DOMAIN>/api/controller/zdb/list`
- method: POST
- Body params:
    - *password*: (string) password to access vdc
- Return:
    - *zdbs*: (JSON string) all storage containers information of vdc


## Add new storage node

- `<YOUR_VDC_DOMAIN>/api/controller/zdb/add`
- method: POST
- Body params:
    - *password*: (string) password to access vdc
    - *capacity*: (int) size of the storage node to be added in GB e.g 10
    - *farm*(optional): (string) farm to add zdb on
- Return:
    - *wids*: (JSON string) list of workload ids of the new node/s added


## Delete storage node

- `<YOUR_VDC_DOMAIN>/api/controller/zdb/delete`
- method: POST
- Body params:
    - *password*: (string) password to access vdc
    - *wid*: (int) workload id of the storage node to be deleted


## Get vdc prepaid wallet info

- `<YOUR_VDC_DOMAIN>/api/controller/wallet`
- method: POST
- Body params:
    - *password*: (string) password to access vdc
- Return:
    - *wallet*: (JSON string) prepaid wallet information used in vdc


## Get all used pools
- `<YOUR_VDC_DOMAIN>/api/controller/pools`
- method: POST
- Body params:
    - *password*: (string) password to access vdc
- Return:
    - *pools*: (JSON string list) all active pools' information used in the vdc


## Get alerts
- `<YOUR_VDC_DOMAIN>/api/controller/alerts`
- method: POST
- Body params:
    - *password*: (string) password to access vdc
    - *application*(optional): application type to filter alerts with
- Return:
    - *alerts*: (JSON string) all alerts on vdc threebot machine
