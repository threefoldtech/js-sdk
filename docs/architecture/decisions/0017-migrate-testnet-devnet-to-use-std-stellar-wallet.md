# 17. Migrate testnet, devnet to use STD stellar wallet

Date: 2020-12-30

## Status

Accepted

## Context

Stellar testnet network is overloaded recently and causes a lot of delay and errors

## Decision

Using Stellar Mainnet network (STD TFT). But prices will vary according to the explorer type, example: (devnet would cost 1% from mainnet, testnet would cost 10% from mainnet price)

## Consequences

- Deprecate testnet wallets and apps (staging app) for payments.
- Use stellar STD stable network
