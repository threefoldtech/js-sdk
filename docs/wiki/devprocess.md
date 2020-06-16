# Development process for any threefoldtech projects

Projects are defined in threefoldtech/project tab in github

## Branches

- master: to release from
- development: where everyone branch from (nothing gets committed directly on development except for hotfixes)

## Branching strategy

- For new feature defined in the milestone, we branch of development branch with `development_featurename` and when done a PR against development that needs to pass all of the checks we implemented on the repository.
- In case of multiple users working together on the same feature use `merges` 
- In case of a single user working on a feature, it's okay to `rebase` your branch on the latest hotfixes pushed on development
- If your feature affecting other people it gets merged into `integration` branch that's updated daily from development fixes and when all affected stories are done we test the integration branch before merging them in.

## Contribution
Check [contribution](./contribution.md) page and [coding/documentation style](./codingstyle.md)