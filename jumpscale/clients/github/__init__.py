def export_module_as():
    from jumpscale.core.base import StoredFactory
    from .github import GithubClient

    return StoredFactory(GithubClient)
