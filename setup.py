from setuptools import find_packages, setup

from version import __version__

DATA = [
    "blueprint/admin/static/js/api/*",
    "blueprint/admin/static/js/route/*",
    "blueprint/admin/static/js/utils/*",
    "blueprint/admin/templates/*",
    "blueprint/admin/templates/admin/*",
    "blueprint/admin/templates/includes/*",
    "i18n/translations/*",
    "mail/template/*",
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
