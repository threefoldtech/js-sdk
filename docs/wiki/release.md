## Releasing js-sdk process

- Create a branch `development_VERSION`
- Verify code on development branch `make tests`
- Generate documentation `make docs`
- Update js-sdk version in `pyproject.toml` to the branch version
- Create a pull request aganist the development branch
- Merge the pull request into development
- Create a pull request from development against the master branch
- Merge the pull request into master
- Tag the new version (can be done from the github UI) easier for release notes.
- Build the package `poetry build`
- Publish the package to `pypi.org` using `poetry publish`
