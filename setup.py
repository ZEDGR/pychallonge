from distutils.core import setup
import challonge


setup(name = "pychallonge",
      author = "Russ Amos",
      url = "http://github.com/maxwasserman/pychallonge",
      version = challonge.__version__,
      packages = [
          'challonge',
      ],
      install_requires = [
      ]
)
