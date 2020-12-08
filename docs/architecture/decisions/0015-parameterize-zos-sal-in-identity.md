# 15. parameterize zos sal in identity

Date: 2020-10-07

## Status

Accepted

## Context

Parameterize zos sal in identity so if we want to switch identity at certain point we can for example to deploy workloads with that identity

## Decision

- Make zos sal paramertized with specific identity. If not passed it will use the default identity

## Consequences

- ZOS sal is parametrized with identity which can used to sign/deploy workloads
- Change all usage of zos sal usage to use .get(identity)
