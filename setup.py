from setuptools import find_packages, setup


def find_requirements() -> list[str]:
    with open("requirements.txt") as f:
        return f.read().splitlines()


setup(
    name="web-framework",
    url="https://github.com/enlarge-online/web-framework",
    author="H.P. Mertens",
    python_requires=">=3.11",
    install_requires=find_requirements(),
    include_package_data=True,
    package_data={"": ["mail/template/*", "i18n/translations/*"]},
    packages=find_packages(include=["web", "web.*"]),
)
