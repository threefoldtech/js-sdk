### test01_create_pool_with_funded_wallet

Test for creating a pool with funded wallet.

**Test Scenario**

- Get wallet.
- Create a pool.
- Pay for this pool.
- Check that the pool has been created.
- Check that the token has been transferred from the wallet.

### test02_extend_pool_with_funded_wallet

Test for extending a pool with funded wallet.

**Test Scenario**

- Get wallet.
- Extend an existing pool.
- Pay for the pool.
- Check that the pool has been extended.
- Check that the token has been transferred from the wallet.

### test03_create_pool_with_empty_wallet

Test for creating a pool with empty wallet.

**Test Scenario**

- Create empty wallet.
- Create a pool.
- Pay for the pool, should fail.
- Check that the pool has been created with empty units.

### test04_extend_pool_with_empty_wallet

Test for extending a pool with empty wallet.

**Test Scenario**

- Create empty wallet.
- Extend existing pool.
- Pay for the pool, should fail.
- Check that the pool has not been extended.
