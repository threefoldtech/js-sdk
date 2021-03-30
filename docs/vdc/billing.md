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
- In any new chatflow, the user select from multiple flavors with different prices for 1 month.
- The amount that user paid transferred to the `prepaid_wallet`.
- We replace the `provisioning_wallet` with the `vdc_init` wallet to use it in deploying one hour.
- If VDC deployed successfully, we switch back to the `provisioning_wallet`.
- Transfer half amount from the `prepaid_wallet` to the `provisioning_wallet`.
- Return back all the initial transaction to the `vdc_init` wallet from the `provisioning_wallet`.
-

### Extend VDC

### Grace Period

## Background Services
