# 2. Block misbehaving nodes

Date: 2020-09-07

## Status

Accepted

## Context

Because of failures on zos side e.g [zdb address in use](https://github.com/threefoldtech/zos/issues/916) and [failed to retrieve owner of vollume](https://github.com/threefoldtech/zos/issues/919) We need a feature to block specific nodes or specific farms that acting weird or with low performance


## Decision

When deploying every threebot is aware of failing nodes, and maintains a disallow list typically blocking failing nodes for 4 hours.

## Consequences

### the good
- Smoothen the deployment experience and keep track of failing nodes for reporting
- Will make farmers maintain their farms more

### the worrying

for testing in limited net e.g devnet, or testnet we might get into scenario where you can't deploy anything, but envs should be maintained anyhow.