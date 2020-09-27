# 8. add_kwargs_to_3bot_start

Date: 2020-09-27

## Status

Accepted

## Context

Adding packages with kwargs has some limitations and hence kwargs are needed every time start is called not only once when adding package.

## Decision

Add kwargs passed to the package instance that will be saved locally, and can be retrieved everytime the threebot server restarts and starts the package.

## Consequences

Any package that is added with kwargs will save them and hence with every restart of the package, they are reloaded and used in the install of the package.
