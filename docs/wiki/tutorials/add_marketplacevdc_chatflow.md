# Add New VDC dashboard Chatflow

## Index

- [The structure of the chatflow file](#The-structure-of-the-chatflow-file)

## The structure of the chatflow file
1. Create file with your app name `{app_name}.py` in `packages/vdc_dashboard/chats` directory.
2. You have to inherit from `SolutionsChatflowDeploy` baseclass.

    ```python
    from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy
    class AppDeploy(SolutionsChatflowDeploy):
    ```
3. Define your `solution type` name, `helm repo` name and chatflow `title` that will be shown in frontend

    ```python
        SOLUTION_TYPE = "{app_name}"
        HELM_REPO_NAME = "{repo_name}"
        title = "App Title"
    ```
4. The `CHART_LIMITS` defined in `solutions_chatflow` sals, but it can be overwritten in your chatflow with your custom one like:
    ```python
        CHART_LIMITS = {
            "Silver": {"cpu": "2000m", "memory": "2024Mi"},
            "Gold": {"cpu": "4000m", "memory": "4096Mi"},
            "Platinum": {"cpu": "4000m", "memory": "8192Mi"},
        }
    ```
    - And also `RESOURCE_VALUE_TEMPLATE` the same.
4. Define your chatflow steps:
    ```python
        steps = [
            "init_chatflow",      #required
            "get_release_name",   #required
            "choose_flavor",      #required
            "set_config",
            "create_subdomain",   #required
            "install_chart",      #required
            "initializing",       #required
            "success",            #required
        ]
    ```
    - All steps methods should be decorated with `@chatflow_step(title="")`
    - We defined some required steps in chatflow baseclass, you have to put them in your steps `[ "init_chatflow", "get_release_name", "choose_flavor", "create_subdomain", "install_chart", "success"]`.
    - Before the `install_chart` step additional steps like `set_config`, they can be addded to update `self.config.chart_config` object with your optional configurations.
5. Every deployment will has its own config instance from the start to the end fo the chatflow.
    - This `config` instance will be structured like:
    ```python
    class ChartConfig(Base):
        cert_resolver = fields.String(default="le")
        domain = fields.String(default=None)
        domain_type = fields.String()
        resources_limits = fields.Typed(dict, default={})
        backup = fields.String(default="vdc")
        ip_version = fields.String(default="IPv6")
        extra_config = fields.Typed(dict, default={})


    class DeploymentConfig(Base):
        username = fields.String()
        release_name = fields.String()
        chart_config = fields.Object(ChartConfig)
    ```
    - In the `init_chatflow` step it will be define:
    ```python
    self.config = DeploymentConfig()
    ```
6. In the `Install_chart` step, the `chart_config` variable defined with default configuration and will be updated with the result of `get_config()` function.
    - The default `config_chart` will be:
    ```python
    chart_config = {
        "solution_uuid": self.solution_id,
        "threefoldVdc.backup": self.config.chart_config.backup,
        "global.ingress.certresolver": self.config.chart_config.cert_resolver,
        "resources.limits.cpu": self.config.chart_config.resources_limits["cpu"],
        "resources.limits.memory": self.config.chart_config.resources_limits["memory"],
    }
    ```
    - *HINT:* You can overwrite `get_config` function to return your chart custom configuration as `dict` and the `chart_config` will be updated with before the installation.

7. At the end of the file, you have to add reference for your chat class with reference name `chat`

    ```python
    chat = AppDeploy
    ```
