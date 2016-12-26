from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md")) as f:
    long_description = f.read()

setup(name = "pychal",
    description = "Drop-in replacement of pychallonge",
    long_description = long_description,
    author = "ZEDGR",
    author_email = "georlema@gmail.com",
    url = "https://github.com/ZEDGR/pychal",
    download_url = "https://github.com/ZEDGR/pychal/tarball/1.7.0",
    license = "Public Domain",
    version = "1.7.0",
    keywords = ['tournaments', 'challonge'],
    packages = find_packages(),
    platforms=['any'],
    classifiers = [
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    install_requires = [
        'iso8601',
        'requests',
    ],
)
