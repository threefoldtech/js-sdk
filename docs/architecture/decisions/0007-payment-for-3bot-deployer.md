# 7. payment_for_3Bot_deployer

Date: 2020-09-15

## Status

Accepted

## Context

The deployment of 3Bot is not guaranteed to succeed due to network failures or misbehaving of nodes on the grid. Users who pay for a 3Bot reserve capacity and in case of failing to initialize the solution they lose their money (and that capacity won't be usable after payment)

## Decision

- 3Bot deployer to start with a funded wallet 
- when the user wants to create an instance, we create a pool for this instance using the funded wallet for 15 mins (that should be enough for the initialization step).
- When we manage to deploy and initialize the 3Bot, we ask the user to extend the lifetime of the 3Bot in the same chatflow
- In case of pool extension failure they will be refunded from the explorer


## Consequences

- Users will guarantee their payment won't be lost.
- A small amount of tokens might be lost from our wallet but it guarantees the safety of users payments and successful deployment of their solutions.
