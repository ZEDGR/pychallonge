from setuptools import setup, find_packages
from os import path

cwd = path.abspath(path.dirname(__file__))

with open(path.join(cwd, "README.md")) as f:
    readme = f.read()

setup(
    name="pychallonge",
    description="Α python module to use the Challonge API",
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
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    install_requires=[
        "iso8601==0.1.12",
        "tzlocal>=2.0.0,<3.0",
        "pytz==2019.3",
        "requests>=2.25.1,<3.0",
    ],
)
