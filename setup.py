from os import path

from setuptools import find_packages, setup

cwd = path.abspath(path.dirname(__file__))

with open(path.join(cwd, "README.md")) as f:
    readme = f.read()

setup(
    name="pychallonge",
    description="A python module to use the Challonge API",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="ZEDGR",
    author_email="georlema@gmail.com",
    url="https://github.com/ZEDGR/pychallonge",
    license="Public Domain",
    version="1.11.5",
    keywords=["tournaments", "challonge"],
    packages=find_packages(),
    platforms=["any"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: Public Domain",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],
    install_requires=[
        "iso8601==0.1.12",
        "tzlocal>=2.0.0,<3.0",
        "pytz==2019.3",
        "requests>=2.25.1,<3.0",
    ],
)
