# 20. Dynamically get branch for threebot deployer

Date: 2021-01-19

## Status

Accepted

## Context

In threebot deployer we hardcode the branch we deploy from in the code, this will be annoying if we need to deploy from another branch.

## Decision

Getting the branch dynamically from the active branch of js-sdk repository

## Consequences

Making it easier to get the branch to deploy from instead of hardcoding it. if it fails to get it, it will use development as usual
