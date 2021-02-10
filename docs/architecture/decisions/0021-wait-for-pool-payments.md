# 21. Wait for pool payments

Date: 2021-01-19

## Status

Accepted

## Context

Pools payment can fail due to stellar transaction submission timeout.

## Decision

Since the endpont `https://<explorer-url>/api/v1/reservations/pools/payment/<pool-id>` is deployed now, A wait method is added to wait for the payment info until it's done successfully

## Consequences

Pools payment chances to success are increased unless all retries fail
