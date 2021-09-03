# Add New Marketplace Chatflow

## Index

- [The structure of the chatflow file](#The-structure-of-the-chatflow-file)
- [Define your list app method](#Define-your-list-app-method)
- [Add app in frontend](#Add-app-in-frontend)

## The structure of the chatflow file
1. Create file with name `{your_app_name}.py` in `packages/marketplace/chats` directory.
2. You have to inherit from `MarketPlaceAppsChatflow` baseclass.

    ```python
    class AppDeploy(MarketPlaceAppsChatflow):
    ```
3. Define your `solution type` name and chatflow `title` that will be shown in frontend

    ```python
        SOLUTION_TYPE = "{app_name}"
        title = "App Title"
    ```
4. Define the `query` your app needs.
    ```python
        self.query = {"cru": 1, "mru": 1, "sru": 1}
    ```
3. Define your chatflow steps:
    ```python
        steps = [
            "get_solution_name", # required
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
    - We defined some required steps in chatflow baseclass, you have to put them in your steps `[ "get_solution_name", "solution_expiration", "payment_currency", "infrastructure_setup", "success"]`.

    - After `solution_name` step, put the extra info steps required for your app.
    - In `overview` step, you define your app metadata to be confirmed by the user
        - For example:
            ```python
            @chatflow_step(title="Deployment Information")
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

4. At the end of the file, you have to add reference for your chat class with reference name `chat`

    ```python
    chat = AppDeploy
    ```

## Define your list app method
- Add your `list_{SOLUTION_TYPE}_method` in `sals/marketplace/solutions` module to list all your instances and use in the frontend or shell.
    - `SOLUTION_TYPE` that you defined in the previous step.
- And for returning your solution count should append your `{SOLUTION_TYPE}` in the `count_dict` in `count_solutions` method in the same module

## Add app in frontend
- In the frontend, you just need to add your app object as below in `apps` dict under the section you want to list your app in `packages/marketplace/frontend/data.js`
    - If you need to add another section, just create new one in the `SECTIONS` object with the same structure:
        ```js
        "SECTION NAME": {
            titleToolTip: "Tooltip shown on hovering on section title in the frontend",
            apps: {
                // list your applications objects as below structure
                "App Name": {
                    name: "App Name in frontend",
                    type: "{SOLUTION_TYPE}", // defined in the previous steps
                    image: "./assets/appImage.png", // add your app image in the assets dir
                    disable: false, // make it true if you want to hide your app in the marketplace frontend
                    helpLink: "https://now10.threefold.io/docs", // link to application manual
                    description: "Description of your application"
                },
            },
        },
        ```
    - If you just need to add your application in an existing section, add a new app object with below structure in the section object you want to list in:
        ```js
        {
            "App Name": {
                name: "App Name in frontend",
                type: "{SOLUTION_TYPE}", // defined in the previous steps
                image: "./assets/appImage.png", // add your app image in the assets dir
                disable: false, // make it true if you want to hide your app in the marketplace frontend
                helpLink: "https://now10.threefold.io/docs", // link to application manual
                description: "Description of your application"
            },
        }
        ```
