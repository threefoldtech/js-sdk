# Add New VDC dashboard Chatflow

## Index

- [The structure of the chatflow file](#The-structure-of-the-chatflow-file)

## The structure of the chatflow file
1. Create file with name `{your_app_name}.py` in `packages/vdc_dashboard/chats` directory.
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
4. Define your chatflow steps:
    ```python
        steps = [
            "get_release_name",   #required
            "select_vdc",         #required
            "create_subdomain",   #required
            "set_config",
            "install_chart",      #required
            "initializing",       #required
            "success",            #required
        ]
    ```
    - All steps methods should be decorated with `@chatflow_step(title="")`
    - We defined some required steps in chatflow baseclass, you have to put them in your steps `[ "get_release_name", "select_vdc", "create_subdomain", "install_chart", "success"]`.
    - Before the `install_chart` step an addtional step can be addded that includes:
        - Call `self._choose_flavor()` to ask the user for the solution's resources limits.
        - Update `self.chart_config` dict with your optional configurations.

5. At the end of the file, you have to add reference for your chat class with reference name `chat`

    ```python
    chat = AppDeploy
    ```
