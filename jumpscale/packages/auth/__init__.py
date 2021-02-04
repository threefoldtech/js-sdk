"""
# Auth package is responsible for making authentication and authorization using ThreeFold Connect

## Components

### package.toml

- Conains the nginx locations for the package for template static files under `static` and reverse proxy

### Bottle app

- In `bottle/auth.py` it has the main methods used to create the authentication

### Templates

- In `bottle/templates` There are 3 templates
  - home.html: the main structure of the auth page
  - login.html: the login component shows all available providers to login in with (ThreeFold Connect)
  - access_denied.html: this page is when the user is not authorized to view this page

### Authentication flow:

  - You need to put the login_required decorator on the required route to secure
    example in chatflow package.
    ```
    @app.route("/<package_name>")
    @login_required
    def chats(package_name):
    ```

  - This decorator checks if threebot_connect* is enabled if so then it redirects you to the login url

  - Then `login` method takes over, it renders the template takes the required provider and redirects to it

  - After that the response is back to the callback method, it verify the identity of the user and redirect to the requested url

* To enable threebot_connect(enabled by default): `j.core.config.set('threebot_connect', True)`
* To disable threebot_connect: j.core.config.set('threebot_connect', False)


"""
