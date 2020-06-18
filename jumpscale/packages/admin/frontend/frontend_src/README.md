# Admin dashboard

Admin dashboard UI based on [webix jet](https://webix.gitbook.io/webix-jet/).

## Dependencies

* nodejs & npm
* `cd frontend_src`
* `npm install`

## Development

While development, 3Bot needs to be started with this package installed, then for building the front-end with source maps as a development build, you can use `build_frontend.sh`:

```bash
cd frontend_src && bash build_frontend.sh dev
```

This script will build and copy the output to `frontend` directory to be served as a single page app,then you can go to `http://<host>/admin`.

For production builds, don't pass `dev` to the script:

```bash
bash build_frontend.sh
```

Make sure to push production builds after you finish updating frontend source.

## Structure

* The main entry is [app.js](sources/app.js)
* Views:
  * Main view is defined at [main.js](sources/views/main.js)
  * External views are [wiki](sources/views/wikis), [codeserver](sources/views/codeserver) and [jupyter](sources/views/jupyter).
* Services (calling backend/actors) can be found at [sources/services](sources/services).

## Walktrough creating new component

### MainView

Main view is defined at [main.js](sources/views/main.js) it contains the sidebar stuff and gathers the whole app in it.

### Add entry to sidebar

#### Let's take example `codeserver`:

* Add a directory for your view with under `/soruces/views`
*
    ![codeserver](./images/codeserver.png)

* Then in index.js define your view. example

    ```javascript
    import { ExternalView } from "../external";

    const CODE_URL = "/codeserver/?folder=/sandbox/code";
    const REQUIRED_PACKAGES = {
        "zerobot.codeserver": "https://github.com/threefoldtech/jumpscaleX_threebot/tree/development/ThreeBotPackages/zerobot/codeserver"
    }

    export default class CodeserverView extends ExternalView {
        constructor(app, name) {
            super(app, name, CODE_URL, REQUIRED_PACKAGES);
        }
    }
    ```

* Now we have the view, to be able to access it we need to add an entry in the sidebar to access it

* in [main.js](sources/views/main.js) there is a list `sidebarData` we can append a view or a view with subviews

    ```javascript
    {
        id: "codeserver",
        value: "Codeserver",
        icon: "mdi mdi-code-tags"
    }
    ```

* this will add a view with id dash (must be the same view directory), and defines icon of from webix

#### Let's take another example for subviews
