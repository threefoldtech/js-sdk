# Deploy Ubuntu in the grid

## Requirements

Please check the [general requirements](https://sdk.threefold.io/#/sdk__code)

## Create your network

please follow the instructions [here](https://sdk.threefold.io/#/sdk__code_network)

## deploy ubuntu container access using ssh

please follow the instructions [here](https://sdk.threefold.io/#/sdk__code_container)

But only replace `flist` parameter with `https://hub.grid.tf/tf-bootable/3bot-ubuntu-20.04.flist`
## deploy ubuntu container access using Web only COREX

As mention in the previous section, but assign `interactive` with `True`.

## access your ubuntu container using ssh

```bash
ssh roo@<ip_address>
```

## access your ubuntu container using web

```bash
<ip_address>:7681
```
- run bash  to goto into container
```bash
<ip_address>:7681/api/process/start?arg[]=/bin/bash
```
Then refresh page and press on job id
