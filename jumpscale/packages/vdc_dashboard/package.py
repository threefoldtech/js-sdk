from jumpscale.loader import j


class vdc_dashboard:
    def start(self, **kwargs):
        # Configuring 3bot deployer package actors to be public
        location_actors_443 = j.sals.nginx.main.websites.default_443.locations.get(name="vdc_dashboard_controller")
        location_actors_443.is_auth = False
        location_actors_443.is_admin = False
        location_actors_443.is_package_authorized = False
        location_actors_443.save()

        location_actors_80 = j.sals.nginx.main.websites.default_80.locations.get(name="vdc_dashboard_controller")
        location_actors_80.is_auth = False
        location_actors_80.is_admin = False
        location_actors_80.is_package_authorized = False
        location_actors_80.save()

        j.sals.nginx.main.websites.default_443.configure()
        j.sals.nginx.main.websites.default_80.configure()
