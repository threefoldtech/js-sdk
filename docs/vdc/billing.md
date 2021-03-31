# VDC Billing

In this manual we will mention a detailed information about billing in VDC and its flow from user and deployer perspective according to our **business plan**.

## Important Keywords

We will use the following keywords:
- **vdc_init wallet**: [see in](./vdc_deployer#requirements)
- **grace_period wallet**: [see in](./vdc_deployer#requirements)
- **prepaid_wallet**: Wallet used by the user, S/He has its secret and a full control on it.
- **provisioning_wallet**: Wallet used by the deployer to fund the pool.
- **user_price**: The price that deployer configure it for each plan.
- **farm_price**: The price that farmer set for CU/SU units.

## Flow

### New VDC
1. In any new chatflow, the user select from multiple flavors with different prices for 1 month.
2. The amount that user paid transferred to the `prepaid_wallet`.
3. We replace the `provisioning_wallet` with the `vdc_init` wallet to use it in deploying one hour.
4. If VDC deployed successfully, we switch back to the `provisioning_wallet`.
5. Transfer half amount from the `prepaid_wallet` to the `provisioning_wallet`.
6. Return back all the initial transaction to the `vdc_init` wallet from the `provisioning_wallet`.
7. From step 5, the `provisioning_wallet` has funded, In this step if there is a difference between `user_price` and `farm_price` we cover it from `vdc_init` wallet for half a month.
8. After that, 2 background services fund the farm hourly, for more info about [background services](#background-services)

### Renew Plan
The VDC keep alive if the `prepaid_wallet` has a balance for 1 hour to transfer it to the `provisioning_wallet` for the next hour.

### Grace Period
After your VDC expire, we give you a period of time to renew your plan, In this period you can't access your VDC, but all your deployments will be saved.

## Background Services

### Deployer Service
- FundPricesDifference: Run hourly to check that the VDC `prepaid wallet` has fund for 1 hour, it will fund the VDC `provisioning_wallet` with the difference between `user_price` and `farm_price` for 1 hour.

### VDC Service
- TransferPrepaidToProvisionWallet: Run hourly to transfer amount of 1 hour of `user_price` form the `prepaid wallet` to the `provisioning_wallet`.
- AutoExtendbillingService: Run hourly to extend pool from the `provisioning_wallet`.
