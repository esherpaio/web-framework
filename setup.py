from setuptools import setup, find_packages

from version import __version__


def find_requirements() -> list[str]:
    with open("requirements.txt") as f:
        return f.read().splitlines()


setup(
    author="H.P. Mertens",
    include_package_data=True,
    install_requires=find_requirements(),
    name="webshop",
    package_data={"": ["mail/template/*"]},
    packages=find_packages(include=["webshop", "webshop.*"]),
    python_requires=">=3.11",
    url="https://github.com/enlarge-online/webshop-frame",
    version=__version__,
)
