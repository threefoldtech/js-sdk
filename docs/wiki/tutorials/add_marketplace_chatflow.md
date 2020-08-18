# Add New Marketplace Chatflow

## Index

- [The structure of the chatflow file](#The-structure-of-the-chatflow-file)
- [Define your list app method](#Define-your-list-app-method)
- [Add app in frontend](#Add-app-in-frontend)

## The structure of the chatflow file
1. Create file with name `{your_app_name}.py` in `packages/marketplace/chats` directory.
2. You have to inherit from `MarketPlaceChatflow` baseclass.

    ```python
    class AppDeploy(MarketPlaceChatflow):
    ```
3. Define your `solution type` name and chatflow `title` that will be shown in frontend

    ```python
        SOLUTION_TYPE = "{app_name}"
        title = "App Title"
    ```
3. Define your chatflow steps:
    ```python
        steps = [
            "start", # required
            "solution_name", # required
            "app_info_steps",
            "solution_expiration", # required
            "payment_currency", # required
            "infrastructure_setup", # required
            "overview",
            "reservation",
            "success", # required
        ]
    ```
    - All steps methods should be decorated with `@chatflow_step(title="")`
    - We defined some required steps in chatflow baseclass, you have to put them in your steps `["start", "solution_name", "solution_expiration", "payment_currency", "infrastructure_setup", "success"]`.

    - In the `start` step, you have to:
        1. Call `self._init_solution()` in the first line to initialize some props.

        2. Override the value of the `self.query` that your app needs.
            ```python
            @chatflow_step()
            def start(self):
                self._init_solution()
                self.query = {"cru": 1, "mru": 1, "sru": 1}
                self.md_show("# This wizard will help you deploy an App", md=True)
            ```
    - In the `success` step, you have to:
        1. call `self._wgconf_show_check()` in the first line to check if the user need to download new wgconf.
            ```python
            @chatflow_step(title="Success", disable_previous=True, final_step=True)
            def success(self):
                self._wgconf_show_check()
                message = "success message"
                self.md_show(message, md=True)
            ```
    - After `solution_name` step, put the extra info steps required for your app.
    - In `overview` step, you define your app metadata to be confirmed by the user
        - For example:
            ```python
            @chatflow_step(title="Confirmation")
            def overview(self):
                self.metadata = {
                    "Solution Name": self.solution_name,
                    "Network": self.network_view.name,
                    "Node ID": self.selected_node.node_id,
                    "Pool": self.pool_info.reservation_id,
                    "CPU": self.query["cru"],
                    "Memory": self.query["mru"],
                    "IP Address": self.ip_address,
                }
                self.md_show_confirm(self.metadata)
            ```
    - In `reservation` step, you deploy your workloads as your app needs

4. At the end of the file, you have to add reference for youe chat class with reference name `chat`

    ```python
    chat = AppDeploy
    ```

## Define your list app method
- Add your `list_{SOLUTION_TYPE}_method` in `sals/marketplace/solutions` module to list all your instances and use in the frontend or shell.
    - `SOLUTION_TYPE` that you defined in the previous step.
- And for returning your solution count should append your `{SOLUTION_TYPE}` in the `count_dict` in `count_solutions` method in the same module

## Add app in frontend
- In the frontend, you just need to add your app object in `apps` dict in `packages/marketplace/frontend/App.vue`
    ```js
    {
        name: "App Name in frontend",
        type: "{SOLUTION_TYPE}",
        path: "/{your_app_name}",
        meta: { icon: "app_icon" },
    }
    ```
