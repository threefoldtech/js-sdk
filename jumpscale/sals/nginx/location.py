from jumpscale.god import j
from jumpscale.core.base import Base, fields
from .utils import render_config_template
from enum import Enum


class LocationType(Enum):
    STATIC = "static"
    SPA = "spa"
    PROXY = "proxy"


class Location(Base):
    name = fields.String()
    path_url = fields.String()
    is_auth = fields.Boolean(default=False)
    force_https = fields.Boolean(default=False)
    path_location = fields.String()
    index = fields.String()
    ipaddr_dest = fields.String()
    port_dest = fields.Integer()
    path_dest = fields.String()
    location_type = fields.Enum(LocationType)
    scheme = fields.String()

    @property
    def path_cfg_dir(self):
        return f"{self.parent.path_cfg_dir}/{self.parent.instance_name}_locations"

    @property
    def path_cfg(self):
        return f"{self.path_cfg_dir}/{self.instance_name}.conf"

    @property
    def path_web(self):
        return self.parent.path_web

    def write_config(self, content=""):
        if not content:
            content = render_config_template(f"location_{self.location_type}", obj=self)
        j.sals.fs.write_file(self.path_cfg, content)

    def configure(self):
        """Config is a server config file of nginx (in text format)
        """
        j.sals.fs.mkdir(self.path_cfg_dir)

        if self.location_type.value in [LocationType.STATIC.value, LocationType.SPA.value]:
            if not self.path_location.endswith("/"):
                self.path_location += "/"

        self.write_config(self.config)
