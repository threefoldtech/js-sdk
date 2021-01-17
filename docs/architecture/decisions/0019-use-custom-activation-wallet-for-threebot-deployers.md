# 19. Use custom activation wallet for threebot deployers

Date: 2021-01-11

## Status

Accepted

## Context

Activation service fails a lot and that lead to starting online threebot without a wallet

## Decision

Add option to activate the 3bot wallet via custom activation wallet on the deployer in case threefold service activation fails and pass the secret in the secret env

## Consequences

Start threebot with a wallet failure attemps should be less unless the custom activation wallet doesn't have funds too
