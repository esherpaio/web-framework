import os

from flask import Response, make_response, render_template

from web.blueprint.robots import robots_bp
from web.libs.urls import url_for


@robots_bp.route("/robots.txt")
def robots() -> Response:
    template = render_template(
        "robots.txt",
        disallow_urls=["/api/*", "/webhook/*", "/user/*", "/admin/*"],
        sitemap_url=url_for("robots.sitemap", _external=True),
    )
    text = os.linesep.join([x for x in template.splitlines() if x])
    response = make_response(text)
    response.headers["Content-Type"] = "text/plain"
    return response
