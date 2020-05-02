try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description' : 'Expense tracker',
    'author' : 'Austin Weisgrau',
    'url' : 'http://',
    'download_url' : 'http://',
    'author_email' : 'austinweisgrau@gmail.com',
    'version' : '0.1',
    'install_requires' : ['nose'],
    'packages' : ['exptrkr'],
    'scripts' : [],
    'name' : 'exptrkr'
}

setup(**config)
