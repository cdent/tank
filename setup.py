AUTHOR = 'Chris Dent'
AUTHOR_EMAIL = 'cdent@peermore.com'
NAME = 'tiddlywebplugins.tank'
DESCRIPTION = 'Experimenting with Tank'
VERSION = '0.1'


import os

from setuptools import setup, find_packages


setup(
    namespace_packages = ['tiddlywebplugins'],
    name = NAME,
    version = VERSION,
    description = DESCRIPTION,
    long_description = open(os.path.join(os.path.dirname(__file__),
        'README')).read(),
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    url = 'http://pypi.python.org/pypi/%s' % NAME,
    platforms = 'Posix; MacOS X; Windows',
    packages = find_packages(exclude=['test']),
    install_requires = [
        'tiddlywebplugins.oauth',
        'tiddlywebplugins.utils',
        'tiddlywebplugins.templates',
        'tiddlywebplugins.markdown',
        'tiddlywebplugins.whoosher',
        'tiddlywebplugins.logout',
        'markdown-checklist',
        'httpexceptor'
        ],
    zip_safe = False
)
