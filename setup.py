from setuptools import setup, find_packages

from version import __version__

with open("requirements.txt") as f:
    requires = f.read().splitlines()

setup(
    name="webshop",
    version=__version__,
    packages=find_packages(include=["webshop", "webshop.*"]),
    url="https://github.com/enlarge-online/webshop-frame",
    author="H.P. Mertens",
    python_requires=">=3.11",
    install_requires=requires,
    package_data={"": ["mail/template/template.css"]},
    include_package_data=True,
)
