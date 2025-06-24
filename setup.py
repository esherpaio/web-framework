from setuptools import find_packages, setup

from version import __version__

DATA = [
    "*.md",
    "app/javascript/*.js",
    "app/templates/*.html",
    "document/font/*.ttf",
    "i18n/translation/*.json",
    "mail/template/*.html",
]


def find_requirements() -> list[str]:
    with open("requirements.txt") as f:
        lines = f.read().splitlines()
    ignored = ("#", "git+")
    filtered = [x for x in lines if x and not x.startswith(ignored)]
    return filtered


setup(
    name="web-framework",
    url="https://github.com/esherpaio/web-framework",
    version=__version__,
    author="Stan Mertens",
    python_requires=">=3.11",
    install_requires=find_requirements(),
    include_package_data=True,
    package_data={"": DATA},
    packages=find_packages(include=["web", "web.*"]),
)
