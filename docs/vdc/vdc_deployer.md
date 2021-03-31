# VDC Deployer

This manual will go through setting up an environment for vdc deployments and a quick walk through the sals.

## Requirements

- JS-SDK
- Machine with a domain
- Stellar wallets
  - **vdc_init**: Used to fund the initialization of vdcs to make sure it's working to save users money, also it's used to fund the plan differences. (Required asset: TFTs)
  - **grace_period**: Used to fund the 2 weeks grace period. (Required asset: TFTs)
  - **activation_wallet**: Used to activate vdc wallets (provisioning_wallet & prepaid_wallet). (Required asset: XLMs)
- S3 server for backup and restore

## Setup

- Install [JS-SDK](https://threefoldtech.github.io/js-sdk/wiki/#/./quick_start)
- Create/Import the required wallets mentioned in the previous requirements through `jsng` shell

  ```bash
  # activation wallet
  activation_wallet = j.clients.stellar.new("activation_wallet") # you can pass the secret if you have a wallet already, and skip the activation step
  activation_wallet.activate_through_threefold_service()
  activation.save()

  # initialization wallet
  vdc_init = j.clients.stellar.new("vdc_init") # you can pass the secret if you have a wallet already, and skip the activation step
  vdc_init.activate_through_activation_wallet() # we can use `activate_through_threefold_service() too but not available all the time
  vdc_init.save()

  # grace period wallet
  grace_period = j.clients.stellar.new("grace_period") # you can pass the secret if you have a wallet already, and skip the activation step
  grace_period.activate_through_activation_wallet() # we can use `activate_through_threefold_service() too but not available all the time
  grace_period.save()
  ```

- Transfer tokens to the wallets according to needs using stellar client or any other method
- Edit `package.toml` in vdc package with your domain and email address

  ```bash
  domain = "<your domain>"
  letsencryptemail = "<your email>"
  ```

- Configure S3 backup server
  Install [mc](https://docs.min.io/docs/minio-client-quickstart-guide.html) (minio client).

  ```python
  # bucket in [vdc-devnet, vdc-testnet, vdc-mainnet] according to setup
  s3_config = {"S3_URL": "<your-s3-url>", "S3_BUCKET": "<your-bucketname>", "S3_AK": "<your-access-key>", "S3_SK": "<your-secret-key>"}

  j.core.config.set("VDC_S3_CONFIG", s3_config)
  ```

- Enable logs for VDC Dashboards to existing Redis server.

  ```python
  log_config = {"channel_type": "redis", "channel_host": <redis host>, "channel_port": <redis port>}
  j.core.config.set("VDC_LOG_CONFIG", log_config)

- Install `vdc` and `billing` packages through admin dashboard or server shell
- Now visit the domain and you are ready to deploy your first VDC
- More information [here](https://vdc.threefold.io/)

## Flow

- User will be prompted to enter a vdc name & flavor from the chosen ones
  - If the name is not existed before, The deployer will create a new clean vdc
  - If the name is existed before, The deployer will restore from the latest taken backup. (This may take few minutes)
- Then User will be prompted to pay the amount of the vdc per month (Prices will be different accross the networks devnet, testnet, mainnet)
- The deployer will deploy the following:
  - Kubernetes cluster with the selected flavors and it will have a public IP
  - ZDBs with the size according to plan
  - 3Bot container with a domain that will be used to access your VDC dashboard
- It will try to deploy on all nodes in the selected farms. In case of failure, the deployer will rollback and refund the tokens back to the user except of the transactions fees
- Once the deployment complete you will have access to VDC dashboard, kubeconfig, quantum storage configs

## Renewing plan

- VDC pricing will be for a month from the date of deployment
- To renew the plan you can head to the wallet information, scan the QR code or transfer the tokens to the prepaid wallet address
- If the plan wasn't renewed in time, User will have a grace period of 2 weeks, The workloads will be up but not accessible
- If the plan wasn't renewed after the grace period. All workloads will be deleted
- Days taken from grace period will be counted and automatically charged from the prepaid wallet when it has enough balance
