# 8. add_kwargs_to_3bot_start

Date: 2020-09-27

## Status

Accepted

## Context

Adding packages with kwargs has some limitations and hence kwargs are needed every time start is called not only once when adding package.

## Decision

Pass kwargs to start method so it will be passed when adding a package until starting the package.

## Consequences

start can take kwargs and other packages will not be affected therefore its backward compatible
