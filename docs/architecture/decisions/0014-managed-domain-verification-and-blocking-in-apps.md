# 14. managed domain verification and blocking in apps

Date: 2020-10-04

## Status

Accepted

## Context

There is no validation for the managed domains specified in the gateways information on the explorer side. Some of these domains are not delegated properly to the gateway's name server so all subdomains we create using these domains are not populated and not resolvable.

## Decision

Create a test subdomain of each managed domain and verify that the subdomain is resolvable and block managed domains that fail this check for a certain amount of time.

## Consequences

Reduced the possibilty of app deployments going wrong due to a misconfiguration in a gateway's domain.
