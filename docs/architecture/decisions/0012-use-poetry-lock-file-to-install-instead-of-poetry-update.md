# 12. Use poetry lock file to install instead of poetry update

Date: 2020-10-01

## Status

Accepted

## Context

Dependancies versions update can lead to failure. They needed to be tested well before using them. Poetry update bumps version to latest each time to execute and takes a long time

## Decision

- Use poetry lock file to install dependancies using specific versions instead of executing poetry update each time

- Updating versions will be by the repository maintainers after making sure no compitablity issues

## Consequences

- Versions are static and tested well so no dependancies version compatiblity issues.
- Reducing js-sdk installation time
