from setuptools import setup, find_packages

setup(name = "pychal",
    description = "Drop-in Replacement of pychallonge",
    author = "ZEDGR",
    author_email = "georlema@gmail.com",
    url = "https://github.com/ZEDGR/pychal",
    download_url = "https://github.com/ZEDGR/pychal/tarball/1.6.5",
    license = "Public Domain",
    version = "1.6.7",
    keywords = ['tournaments', 'challonge'],
    packages = find_packages(),
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
