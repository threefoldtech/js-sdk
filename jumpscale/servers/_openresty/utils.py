from jumpscale.loader import j


DIR_PATH = j.sals.fs.dirname(j.sals.fs.realpath(__file__))
env = j.tools.jinja2.get_env(j.sals.fs.join_paths(DIR_PATH, "templates"))


def render_config_template(name, **kwargs):
    return env.get_template(f"{name}.conf").render(**kwargs)
