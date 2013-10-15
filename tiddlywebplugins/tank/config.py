"""
Base config for tank.
"""

config = {
    'extractors': ['http_basic', 'tiddlywebplugins.tank.extractor'],
    'auth_systems': ['tiddlywebplugins.tank.challenger'],
    'logged_in_redirect': '/dash',
}
