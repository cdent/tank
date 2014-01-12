"""
Stubbing in the stubs.
"""

from tiddlyweb.util import merge_config

from tiddlywebplugins.oauth import init as oauth_init
from tiddlywebplugins.utils import replace_handler

from .config import config as tank_config
from .home import home, dash
from .register import register
from .wiki import wiki_page

def establish_web(config):
    oauth_init(config)

    selector = config['selector']
    replace_handler(selector, '/', dict(GET=home))
    selector.add('/dash', GET=dash)
    selector.add('/register', POST=register)
    selector.add('/tanks/{bag_name:segment}[/{tiddler_name:segment}]',
            GET=wiki_page)

def init(config):
    merge_config(config, tank_config, reconfig=True)
    if 'selector' in config:
        establish_web(config)
