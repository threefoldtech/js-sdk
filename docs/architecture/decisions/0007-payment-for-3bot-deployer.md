# 7. payment_for_3Bot_deployer

Date: 2020-09-15

## Status

Accepted

## Context

The deployment of 3Bot is not guaranteed due to network failures or misbehaving of nodes so users reserve the capacity and the solution fails to initialize so they lose their money

## Decision

we have a funded wallet on 3bot deployer
when the user wants to create an instance, we can create a pool for this instance using this wallet for 15 mins.
then in success case, the user will be asked for extending in the same chatflow. And in case of failure, they will be refunded from the explorer for the failure from extending the pool.

## Consequences

- Users will guarantee that that their payment won't be lost.
- A small amount of tokens will be lost from our wallet but it guarantees the safety of users payments and successful deployment of their solutions.
