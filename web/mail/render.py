import os

import jinja2

from web.config import config


def render_email(name: str = "default", **attrs) -> str:
    dir_ = os.path.dirname(os.path.realpath(__file__))
    loader = jinja2.FileSystemLoader(dir_)
    environment = jinja2.Environment(loader=loader)
    fp = os.path.join("template", f"{name}.html")
    attrs.update({"config": config})
    html = environment.get_template(fp).render(attrs)
    return html
