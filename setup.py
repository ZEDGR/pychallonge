from distutils.core import setup
import challonge


setup(name = "pychal",
      author = "ZEDGR",
      author_email = "georlema@gmail.com",
      url = "https://github.com/ZEDGR/pychal",
      version = challonge.__version__,
      keywords = ['tournaments', 'challonge'],
      packages = [
          'challonge',
      ],
      install_requires = [
          'iso8601>=0.1.11',
          'requests>=2.9.0',
      ]
)
