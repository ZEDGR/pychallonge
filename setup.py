from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.rst")) as f:
    long_description = f.read()

setup(name = "pychal",
    description = "Drop-in replacement of pychallonge",
    long_description = long_description,
    author = "ZEDGR",
    author_email = "georlema@gmail.com",
    url = "https://github.com/ZEDGR/pychal",
    license = "Public Domain",
    version = "1.10.0",
    keywords = ['tournaments', 'challonge'],
    packages = find_packages(),
    platforms=['any'],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    install_requires = [
        'iso8601==0.1.12',
        'tzlocal==2.0.0',
        'pytz==2019.3',
        'requests==2.23.0',
    ],
)
