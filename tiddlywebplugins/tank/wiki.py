"""
Wiki things.
"""

from httpexceptor import HTTP404, HTTP302, HTTP400

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.policy import Policy, PermissionsError
from tiddlyweb.model.tiddler import Tiddler, current_timestring
from tiddlyweb.store import NoBagError, NoTiddlerError
from tiddlyweb.web.util import get_route_value, encode_name, server_base_url
from tiddlyweb.wikitext import render_wikitext

from tiddlywebplugins.templates import get_template

WIKI_TEMPLATE = 'wiki.html'
EDIT_TEMPLATE = 'edit.html'


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



def create_wiki(environ, name, mode='private', username=None):
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
    store.put(bag)

    return bag


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
    try:
        tiddler = store.get(tiddler)
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

    store.put(tiddler)

    redirect_uri = tank_page_uri(environ, tiddler.bag, tiddler.title)

    start_response('303 See Other', [
        ('Location', str(redirect_uri))])

    return []


def editor(environ, start_response):
    store = environ['tiddlyweb.store']
    usersign = environ['tiddlyweb.usersign']
    query = environ['tiddlyweb.query']
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
        'user': usersign['name'],
        'tiddler': tiddler,
    })


def tank_uri(environ, tank_name):
    """
    Create a redirect URI for a given tank.
    """
    return server_base_url(environ) + '/tanks/%s' % encode_name(tank_name)


def tank_page_uri(environ, tank_name, tiddler_title):
    """
    Create a redirect URI for a given page/tiddler within a tank.
    """
    return tank_uri(environ, tank_name) + '/%s' % encode_name(tiddler_title)


def wiki_page(environ, start_response):
    """
    Present a single tiddler from a given tank.
    """
    store = environ['tiddlyweb.store']
    usersign = environ['tiddlyweb.usersign']
    tank_name = get_route_value(environ, 'bag_name')

    try:
        bag = store.get(Bag(tank_name))
    except NoBagError:
        raise HTTP404('no tank found for %s' % tank_name)

    try:
        tiddler_name = get_route_value(environ, 'tiddler_name')
    except (KeyError, AttributeError):
        raise HTTP302(tank_page_uri(environ, tank_name, 'index'))


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
            'user': usersign['name'],
            'tiddler': tiddler,
            'html': html,
            'bag': bag,
            'edit': editable,
            'delete': deletable,
        })
    else:
        return tiddler_get(environ, start_response)
