from setuptools import find_packages, setup

from version import __version__

DATA = [
    "*.md",
    "app/blueprint/admin_v1/static/*.css",
    "app/blueprint/admin_v1/static/*.js",
    "app/blueprint/admin_v1/templates/*.html",
    "app/blueprint/admin_v1/templates/admin/*.html",
    "app/blueprint/admin_v1/templates/admin/section/*.html",
    "app/blueprint/auth_v1/static/*.js",
    "app/blueprint/auth_v1/templates/*.html",
    "app/blueprint/auth_v1/templates/auth/*.html",
    "app/blueprint/robots_v1/templates/*.txt",
    "app/blueprint/robots_v1/templates/*.xml",
    "app/static/*.js",
    "app/templates/*.html",
    "document/font/*.ttf",
    "i18n/translation/*.json",
    "mail/template/*.html",
]


def find_requirements() -> list[str]:
    with open("requirements.txt") as f:
        lines = f.read().splitlines()
    return [x for x in lines if x and not x.startswith("#")]


setup(
    name="web-framework",
    url="https://github.com/esherpaio/web-framework",
    version=__version__,
    author="H.P. Mertens",
    python_requires=">=3.11",
    install_requires=find_requirements(),
    include_package_data=True,
    package_data={"": DATA},
    packages=find_packages(include=["web", "web.*"]),
)
