"""
Base config for tank.
"""

from .util import tank_uri, tank_tiddler_uri, tank_tiddler_resolver

config = {
    'extractors': ['tiddlywebplugins.tank.keyextractor',
        'tiddlywebplugins.oauth.extractor',
        'tiddlywebplugins.tank.extractor'],
    'auth_systems': ['tiddlywebplugins.tank.challenger'],
    'logged_in_redirect': '/dash',
    'wikitext.default_renderer': 'tiddlywebplugins.markdown',
    'wikitext.type_render_map': {
        'text/x-markdown': 'tiddlywebplugins.markdown',
        'text/x-tiddlywiki': 'tiddlywebplugins.twikified'
    },
    'use_dispatcher': True,
    'links.at_means_bag': True,
    # Note: whoosher on beanstalk introduces latency issues
    'beanstalk.listeners': ['tiddlywebplugins.jsondispatcher'],
    'markdown.wiki_link_base': '',
    'markdown.interlinker': tank_uri,
    'markdown.transclude_url': tank_tiddler_uri,
    'markdown.target_resolver': tank_tiddler_resolver,
    'markdown.extensions': (['markdown_checklist.extension'], {}),
    'serializers': {
        'text/html': ['tiddlywebplugins.tank.htmlserialization',
            'text/html; charset=UTF-8']
    },
    # cors
    'cors.match_origin': True,
    'cors.allow_creds': True,
    'cors.enable_non_simple': True,
    'cors.exposed_headers': ['X-Tank-Key'],
}
