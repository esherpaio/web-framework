from setuptools import find_packages, setup

from version import __version__

DATA = [
    "blueprint/admin/static/*.html",
    "blueprint/admin/static/css/*.css",
    "blueprint/admin/static/js/*.js",
    "blueprint/admin/templates/*.html",
    "blueprint/admin/templates/admin/*.html",
    "blueprint/admin/templates/admin/section/*.html",
    "blueprint/admin/templates/auth/*.html",
    "blueprint/auth/templates/*.html",
    "blueprint/robots/templates/*.txt",
    "blueprint/robots/templates/*.xml",
    "i18n/translation/*.json",
    "mail/template/*.html",
    "pdf/pdf/canvas/font/composite_font/cmaps/*",
    "pdf/pdf/canvas/font/simple_font/afm/*.afm",
    "pdf/pdf/canvas/font/simple_font/ttf/*.ttf",
    "pdf/pdf/canvas/layout/hyphenation/resources/*.json",
    "pdf/pdf/canvas/lipsum/resources/*.json",
]


def find_requirements() -> list[str]:
    with open("requirements.txt") as f:
        lines = f.read().splitlines()
    return [x for x in lines if x and not x.startswith("#")]


setup(
    name="web-framework",
    url="https://github.com/enlarge-online/web-framework",
    version=__version__,
    author="H.P. Mertens",
    python_requires=">=3.11",
    install_requires=find_requirements(),
    include_package_data=True,
    package_data={"": DATA},
    packages=find_packages(include=["web", "web.*"]),
)
