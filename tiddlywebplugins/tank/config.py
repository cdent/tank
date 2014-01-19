"""
Base config for tank.
"""

from tiddlywebplugins.tank.wiki import (tank_uri, tank_tiddler_uri,
        tank_tiddler_resolver)

config = {
    'extractors': ['http_basic', 'tiddlywebplugins.tank.extractor'],
    'auth_systems': ['tiddlywebplugins.tank.challenger'],
    'logged_in_redirect': '/dash',
    'wikitext.default_renderer': 'markdown',
    'wikitext.type_render_map' :{
        'text/x-markdown': 'tiddlywebplugins.markdown'
    },
    'markdown.wiki_link_base': '',
    'markdown.interlinker': tank_uri,
    'markdown.transclude_url': tank_tiddler_uri,
    'markdown.target_resolver': tank_tiddler_resolver,
    'markdown.extensions': (['markdown_checklist.extension'], {}),
}
