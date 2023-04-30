import re

from setuptools import setup, find_packages

from version import __version__


def find_requirements() -> list[str]:
    requirements = []
    with open("requirements.txt") as f:
        lines = f.read().splitlines()
    for line in lines:
        match = re.fullmatch(r"^git\+https://\w+@github\.com/[\w-]+/([\w-]+)\.git@v([\d.]*)$", line)
        if match:
            line = f"{match.group(1)}=={match.group(2)}"
        requirements.append(line)
    return requirements


setup(
    author="H.P. Mertens",
    include_package_data=True,
    install_requires=find_requirements(),
    name="web",
    package_data={"": ["mail/template/*"]},
    packages=find_packages(include=["web", "web.*"]),
    python_requires=">=3.11",
    url="https://github.com/enlarge-online/web-framework",
    version=__version__,
)
