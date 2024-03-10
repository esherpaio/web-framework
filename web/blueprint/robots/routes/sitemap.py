import itertools

from flask import Response, current_app, make_response, render_template
from sqlalchemy.orm import joinedload

from web.blueprint.robots import robots_bp
from web.database import conn
from web.database.model import Article, Sku
from web.libs.app import is_endpoint
from web.libs.cache import cache
from web.libs.locale import gen_locale
from web.libs.parse import str_to_xml
from web.libs.sitemap import Sitemap, SitemapUrl


@robots_bp.route("/sitemap.xml")
def sitemap() -> Response:
    sitemaps = []
    for rule in current_app.url_map.iter_rules():
        if rule.endpoint and rule.endpoint.startswith("robots.sitemap_"):
            sitemaps.append(Sitemap(rule.endpoint))
    template = render_template("sitemap_index.xml", sitemaps=sitemaps)
    response = make_response(str_to_xml(template))
    response.headers["Content-Type"] = "application/xml"
    return response


@robots_bp.route("/sitemap-pages.xml")
def sitemap_pages() -> Response:
    iter_args = (
        [x for x in cache.countries if x.in_sitemap],
        [x for x in cache.languages if x.in_sitemap],
    )

    urls = []
    for route in cache.routes:
        if not route.in_sitemap or not is_endpoint(route.endpoint):
            continue
        for country, language in itertools.product(*iter_args):
            locale = gen_locale(language.code, country.code)
            sitemap_ = SitemapUrl(route.endpoint, _locale=locale)
            urls.append(sitemap_)

    template = render_template("sitemap.xml", urls=urls)
    response = make_response(str_to_xml(template))
    response.headers["Content-Type"] = "application/xml"
    return response


@robots_bp.route("/sitemap-products.xml")
def sitemap_products() -> Response:
    with conn.begin() as s:
        skus = (
            s.query(Sku)
            .options(joinedload(Sku.route))
            .filter_by(is_deleted=False)
            .order_by(Sku.slug)
            .all()
        )

    iter_args = (
        [x for x in cache.countries if x.in_sitemap],
        [x for x in cache.languages if x.in_sitemap],
    )

    urls = []
    for sku in skus:
        if not is_endpoint(sku.route.endpoint):
            continue
        for country, language in itertools.product(*iter_args):
            locale = gen_locale(language.code, country.code)
            sitemap_ = SitemapUrl(sku.route.endpoint, _locale=locale, slug=sku.slug)
            urls.append(sitemap_)

    template = render_template("sitemap.xml", urls=urls)
    response = make_response(str_to_xml(template))
    response.headers["Content-Type"] = "application/xml"
    return response


@robots_bp.route("/sitemap-articles.xml")
def sitemap_articles() -> Response:
    with conn.begin() as s:
        articles = (
            s.query(Article)
            .options(joinedload(Article.route))
            .filter_by(is_deleted=False)
            .order_by(Article.slug)
            .all()
        )

    iter_args = (
        [x for x in cache.countries if x.in_sitemap],
        [x for x in cache.languages if x.in_sitemap],
    )

    urls = []
    for article in articles:
        if not is_endpoint(article.route.endpoint):
            continue
        for country, language in itertools.product(*iter_args):
            locale = gen_locale(language.code, country.code)
            sitemap_ = SitemapUrl(article.endpoint, _locale=locale)
            urls.append(sitemap_)

    template = render_template("sitemap.xml", urls=urls)
    response = make_response(str_to_xml(template))
    response.headers["Content-Type"] = "application/xml"
    return response
