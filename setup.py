from setuptools import setup, find_packages

from version import __version__


def find_requirements() -> list[str]:
    with open("requirements.txt") as f:
        return f.read().splitlines()


setup(
    author="H.P. Mertens",
    include_package_data=True,
    install_requires=find_requirements(),
    name="Web Framework",
    package_data={"": ["mail/template/*"]},
    packages=find_packages(include=["web", "web.*"]),
    python_requires=">=3.11",
    url="https://github.com/enlarge-online/web-framework",
    version=__version__,
)
