"""
Wiki things.
"""

from httpexceptor import HTTP404, HTTP302, HTTP400

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.policy import Policy, PermissionsError
from tiddlyweb.model.tiddler import Tiddler, current_timestring
from tiddlyweb.store import NoBagError, NoTiddlerError
from tiddlyweb.control import filter_tiddlers
from tiddlyweb.web.util import (get_route_value, encode_name, server_base_url,
        tiddler_etag)
from tiddlyweb.web.validator import validate_bag, InvalidBagError
from tiddlyweb.wikitext import render_wikitext

from tiddlywebplugins.utils import require_role
from tiddlywebplugins.templates import get_template

from .home import dash, gravatar

WIKI_TEMPLATE = 'wiki.html'
EDIT_TEMPLATE = 'edit.html'
CHANGES_TEMPLATE = 'changes.html'

def private_policy(username):
    return Policy(owner=username,
            read=[username],
            write=[username],
            create=[username],
            delete=[username],
            manage=[username],
            accept=['NONE'])


def protected_policy(username):
    return Policy(owner=username,
            read=[],
            write=[username],
            create=[username],
            delete=[username],
            manage=[username],
            accept=['NONE'])


def public_policy(username):
    return Policy(owner=username,
            read=[],
            write=[],
            create=[],
            delete=[],
            manage=[username],
            accept=['NONE'])


WIKI_MODES = {
    'private': private_policy,
    'protected': protected_policy,
    'public': public_policy,
}


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

    tiddlers = filter_tiddlers(store.list_bag_tiddlers(bag),
        'select=modified:>%sd;sort=-modified' % days, environ)

    changes_template = get_template(environ, CHANGES_TEMPLATE)
    start_response('200 OK', [
        ('Content-Type', 'text/html; charset=UTF-8'),
        ('Cache-Control', 'no-cache')])
    return changes_template.generate({
        'days': days,
        'tiddlers': tiddlers,
        'bag': bag,
        'gravatar': gravatar(environ),
        'user': usersign['name'],
    })


SPECIAL_PAGES = {
    'RecentChanges': recent_changes
}


def create_wiki(environ, name, mode='private', username=None, desc='',
        validate=True):
    """
    Create a wiki with the name, name.

    For now a wiki is just a bag a policy.
    """
    store = environ['tiddlyweb.store']
    if username is None:
        username = environ['tiddlyweb.usersign']['name']

    bag = Bag(name)

    # We want this get to fail.
    try:
        store.get(bag)
        return False
    except NoBagError:
        pass

    try:
        bag.policy = WIKI_MODES[mode](username)
    except KeyError:
        bag.policy = WIKI_MODES['private'](username)
    bag.desc = desc
    if validate:
        validate_bag(bag, environ)
    store.put(bag)

    return bag


@require_role('MEMBER')
def forge(environ, start_response):
    """
    Handle a post to create a new tank.
    """
    query = environ['tiddlyweb.query']
    store = environ['tiddlyweb.store']
    usersign = environ['tiddlyweb.usersign']

    try:
        tank_name = query['name'][0]
        tank_policy = query['policy_type'][0]
    except KeyError:
        raise HTTP400('tank_name and tank_policy required')

    tank_desc = query.get('desc', [None])[0]

    try:
        create_wiki(environ, tank_name, mode=tank_policy,
                username=usersign['name'], desc=tank_desc)
    except InvalidBagError as exc:
        return dash(environ, start_response, message='Over quota!')

    uri = tank_uri(environ, tank_name)
    start_response('303 See Other', [
        ('Location', str(uri))])
    return []


def edit(environ, start_response):
    """
    XXX: Lots of duplication from editor.
    """
    store = environ['tiddlyweb.store']
    usersign = environ['tiddlyweb.usersign']
    query = environ['tiddlyweb.query']

    bag_name = query['bag'][0]
    title = query['title'][0]
    text = query['text'][0]
    tags = query['tags'][0]
    etag = query['etag'][0]

    tags = tags.split(', ')

    if not (bag_name and title):
        raise HTTP400('bad query: bag and title required')

    bag = Bag(bag_name)
    try:
        bag = store.get(bag)
    except NoBagError:
        raise HTTP404('that tank does not exist')

    tiddler = Tiddler(title, bag_name)
    tiddler_new = False
    conflict = False
    try:
        tiddler = store.get(tiddler)
        existing_etag = tiddler_etag(environ, tiddler).replace('"', '').split(':', 1)[0]
        print 'etags', etag, existing_etag
        if etag != existing_etag:
            conflict = True
    except NoTiddlerError:
        tiddler.type = 'text/x-markdown'
        tiddler_new = True

    if tiddler_new:
        bag.policy.allows(usersign, 'create')
    else:
        bag.policy.allows(usersign, 'write')

    tiddler.text = text
    tiddler.tags = tags
    tiddler.modifier = usersign['name']
    tiddler.modified = current_timestring()

    if conflict:
        return editor(environ, start_response, tiddler)

    store.put(tiddler)

    redirect_uri = tank_page_uri(environ, tiddler.bag, tiddler.title)

    start_response('303 See Other', [
        ('Location', str(redirect_uri))])

    return []


def editor(environ, start_response, extant_tiddler=None):
    store = environ['tiddlyweb.store']
    usersign = environ['tiddlyweb.usersign']
    query = environ['tiddlyweb.query']

    if extant_tiddler:
        tiddler = extant_tiddler
    else:
        bag_name = query['bag'][0]
        tiddler_title = query['tiddler'][0]

        if not (bag_name and tiddler_title):
            raise HTTP400('bad query: bag and tiddler required')

        bag = Bag(bag_name)
        try:
            bag = store.get(bag)
        except NoBagError:
            raise HTTP404('that tank does not exist')

        tiddler = Tiddler(tiddler_title, bag_name)
        tiddler_new = False
        try:
            tiddler = store.get(tiddler)
        except NoTiddlerError:
            tiddler.text = ''
            tiddler.type = 'text/x-markdown'
            tiddler_new = True

        if tiddler_new:
            bag.policy.allows(usersign, 'create')
        else:
            bag.policy.allows(usersign, 'write')

    edit_template = get_template(environ, EDIT_TEMPLATE)
    start_response('200 OK', [
        ('Content-Type', 'text/html; charset=UTF-8'),
        ('Cache-Control', 'no-cache')])
    return edit_template.generate({
        'conflict': extant_tiddler is not None,
        'user': usersign['name'],
        'tiddler': tiddler,
        'etag': tiddler_etag(environ, tiddler).replace('"', '').split(':', 1)[0]
    })


def tank_uri(environ, tank_name, slash=False):
    """
    Create a redirect URI for a given tank.
    """
    return server_base_url(environ) + '/tanks/%s' % encode_name(tank_name)


def tank_page_uri(environ, tank_name, tiddler_title):
    """
    Create a redirect URI for a given page/tiddler within a tank.
    """
    return tank_uri(environ, tank_name) + '/%s' % encode_name(tiddler_title)


def tank_tiddler_uri(environ, tiddler):
    """
    Create a uri for a given tank page based on a tiddler object.
    """
    return tank_page_uri(environ, tiddler.bag, tiddler.title)


def tank_tiddler_resolver(environ, target, tiddler):
    """
    Modifier a tiddler object to add a bag of the tank named by target.

    Check permissions and let Store and Permission errors raise.
    """
    store = environ['tiddlyweb.store']
    bag = Bag(target)
    bag = store.get(bag)
    bag.policy.allows(environ['tiddlyweb.usersign'], 'read')
    tiddler.bag = target


def wiki_page(environ, start_response):
    """
    Present a single tiddler from a given tank.
    """
    tank_name = get_route_value(environ, 'bag_name')
    store = environ['tiddlyweb.store']
    usersign = environ['tiddlyweb.usersign']

    try:
        bag = store.get(Bag(tank_name))
    except NoBagError:
        raise HTTP404('no tank found for %s' % tank_name)

    try:
        tiddler_name = get_route_value(environ, 'tiddler_name')
    except (KeyError, AttributeError):
        raise HTTP302(tank_page_uri(environ, tank_name, 'index'))

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
        tiddler.text = '## This tiddler does not yet exist\n'
        if creatable:
            editable = True
        deletable = False

    if tiddler.type == 'text/x-markdown':
        html = render_wikitext(tiddler, environ)
        wiki_template = get_template(environ, WIKI_TEMPLATE)
        start_response('200 OK', [
            ('Content-Type', 'text/html; charset=UTF-8'),
            ('Cache-Control', 'no-cache')])
        return wiki_template.generate({
            'gravatar': gravatar(environ),
            'user': usersign['name'],
            'tiddler': tiddler,
            'html': html,
            'bag': bag,
            'edit': editable,
            'delete': deletable,
        })
    else:
        return tiddler_get(environ, start_response)
