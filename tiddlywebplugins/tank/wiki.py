"""
Wiki things.
"""

from httpexceptor import HTTP404, HTTP302

from tiddlyweb.control import filter_tiddlers
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.policy import PermissionsError
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.store import NoBagError, NoTiddlerError
from tiddlyweb.web.handler.tiddler import get as tiddler_get
from tiddlyweb.web.util import get_route_value
from tiddlyweb.util import renderable

from tiddlyweb.wikitext import render_wikitext

from .search import full_search
from .util import (tank_page_uri, get_backlinks, get_rellinks, get_sisterlinks,
        INDEX_PAGE, augment_bag)
from .templates import send_template


WIKI_TEMPLATE = 'wiki.html'
CHANGES_TEMPLATE = 'changes.html'


def recent_changes(environ, start_response):
    """
    List recent changes for the named tank.
    """
    tank_name = get_route_value(environ, 'bag_name')
    store = environ['tiddlyweb.store']
    usersign = environ['tiddlyweb.usersign']
    days = environ['tiddlyweb.query'].get('d', [7])[0]

    try:
        bag = store.get(Bag(tank_name))
        bag.policy.allows(usersign, 'read')
    except NoBagError:
        raise HTTP404('no tank found for %s' % tank_name)

    tiddlers = (store.get(tiddler) for tiddler in
            filter_tiddlers(store.list_bag_tiddlers(bag),
                'select=modified:>%sd;sort=-modified' % days, environ))

    start_response('200 OK', [
        ('Content-Type', 'text/html; charset=UTF-8'),
        ('Cache-Control', 'no-cache')])
    return send_template(environ, CHANGES_TEMPLATE, {
        'days': days,
        'tiddlers': tiddlers,
        'bag': bag,
    })


SPECIAL_PAGES = {
    'RecentChanges': recent_changes
}


def wiki_page(environ, start_response):
    """
    Present a single tiddler from a given tank.
    """
    tank_name = get_route_value(environ, 'bag_name')
    store = environ['tiddlyweb.store']
    usersign = environ['tiddlyweb.usersign']
    config = environ['tiddlyweb.config']

    try:
        bag = store.get(Bag(tank_name))
        bag = augment_bag(store, bag)
    except NoBagError:
        raise HTTP404('no tank found for %s' % tank_name)

    try:
        tiddler_name = get_route_value(environ, 'tiddler_name')
    except (KeyError, AttributeError):
        raise HTTP302(tank_page_uri(environ, tank_name, INDEX_PAGE))

    if tiddler_name in SPECIAL_PAGES:
        return SPECIAL_PAGES[tiddler_name](environ, start_response)

    # let permissions problems raise
    bag.policy.allows(usersign, 'read')

    editable = True
    creatable = True
    deletable = True
    try:
        bag.policy.allows(usersign, 'write')
    except PermissionsError:
        editable = False
    try:
        bag.policy.allows(usersign, 'create')
    except PermissionsError:
        creatable = False
    try:
        bag.policy.allows(usersign, 'delete')
    except PermissionsError:
        deletable = False

    try:
        tiddler = Tiddler(tiddler_name, tank_name)
        tiddler = store.get(tiddler)
    except NoTiddlerError:
        tiddler.type = 'text/x-markdown'
        tiddler.text = '### This tiddler does not yet exist\n'
        if creatable:
            editable = True
        else:
            editable = False
        deletable = False
        if tiddler.title != INDEX_PAGE:
            sisterlinks = get_sisterlinks(environ, tiddler)
            tiddler.text = (tiddler.text
                    + '\n### Other tiddlers with similar names\n' + ''.join(
                    ['* [[%s]]@[[%s]] @%s\n' % (stiddler.title, stiddler.bag,
                        stiddler.bag) for stiddler in sisterlinks]))

    if renderable(tiddler, environ):
        backlinks = get_backlinks(environ, tiddler)
        rellinks = get_rellinks(environ, tiddler)
        compable = full_search(config, 'id:"%s:app"' % tank_name)
        html = render_wikitext(tiddler, environ)
        start_response('200 OK', [
            ('Content-Type', 'text/html; charset=UTF-8'),
            ('Cache-Control', 'no-cache')])
        return send_template(environ, WIKI_TEMPLATE, {
            'tiddler': tiddler,
            'html': html,
            'bag': bag,
            'backlinks': backlinks,
            'create': creatable,
            'edit': editable,
            'delete': deletable,
            'compable': compable,
            'links': rellinks,
        })
    else:
        return tiddler_get(environ, start_response)
