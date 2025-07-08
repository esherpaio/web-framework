import os

import jinja2

from web.setup import settings


def render_email(template: str = "default", dir_: str | None = None, **attrs) -> str:
    if dir_ is None:
        dir_ = os.path.join(os.path.dirname(os.path.realpath(__file__)), "template")
    fn = f"{template}.html"
    loader = jinja2.FileSystemLoader(dir_)
    environment = jinja2.Environment(loader=loader)
    attrs.update({"config": settings})
    html = environment.get_template(fn).render(attrs)
    return html
