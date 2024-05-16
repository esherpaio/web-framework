from setuptools import find_packages, setup

from version import __version__

DATA = [
    "blueprint/admin/static/css/*.css",
    "blueprint/admin/static/js/*.js",
    "blueprint/admin/templates/*.html",
    "blueprint/admin/templates/admin/*.html",
    "blueprint/admin/templates/admin/section/*.html",
    "blueprint/robots/templates/*.txt",
    "blueprint/robots/templates/*.xml",
    "document/base/io/write/document/resources/*.icm",
    "document/base/pdf/canvas/font/composite_font/cmaps/*",
    "document/base/pdf/canvas/font/simple_font/afm/*.afm",
    "document/base/pdf/canvas/layout/emoji/resources/*.png",
    "document/base/pdf/canvas/layout/hyphenation/resources/*.json",
    "document/base/pdf/canvas/lipsum/resources/*.json",
    "i18n/translation/*.json",
    "mail/template/*.html",
]


def find_requirements() -> list[str]:
    with open("requirements.txt") as f:
        return f.read().splitlines()


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
