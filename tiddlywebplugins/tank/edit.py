"""
GET and editor and POST an edit.
"""

from httpexceptor import HTTP400, HTTP404
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler, current_timestring
from tiddlyweb.store import NoBagError, NoTiddlerError
from tiddlyweb.web.util import tiddler_etag
from tiddlyweb.web.validator import InvalidTiddlerError, validate_tiddler

from tiddlywebplugins.templates import get_template

from .home import augment_bag, gravatar
from .csrf import get_nonce
from .util import tank_page_uri


EDIT_TEMPLATE = 'edit.html'


def edit(environ, start_response):
    """
    XXX: Lots of duplication from editor.
    """
    store = environ['tiddlyweb.store']
    usersign = environ['tiddlyweb.usersign']
    query = environ['tiddlyweb.query']

    try:
        bag_name = query['bag'][0]
        title = query['title'][0]
        text = query['text'][0]
        tiddler_type = query['type'][0]
        tags = query['tags'][0]
        etag = query['etag'][0]
    except KeyError as exc:
        raise HTTP400('bad query: incomplete form, %s' % exc)

    tags = [tag.strip() for tag in tags.split(',')]

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
        existing_etag = tiddler_etag(environ, tiddler).replace('"',
                '').split(':', 1)[0]
        if etag != existing_etag:
            conflict = True
    except NoTiddlerError:
        tiddler.type = tiddler_type
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
        return editor(environ, start_response, tiddler,
                message='conflict')

    try:
        validate_tiddler(tiddler, environ)
    except InvalidTiddlerError as exc:
        return editor(environ, start_response, tiddler,
                message='Tiddler content is invalid: %s' % exc)

    store.put(tiddler)

    redirect_uri = tank_page_uri(environ, tiddler.bag, tiddler.title)

    start_response('303 See Other', [
        ('Location', str(redirect_uri))])

    return []


def editor(environ, start_response, extant_tiddler=None, message=''):
    store = environ['tiddlyweb.store']
    usersign = environ['tiddlyweb.usersign']
    query = environ['tiddlyweb.query']
    config = environ['tiddlyweb.config']

    if extant_tiddler:
        tiddler = extant_tiddler
    else:
        try:
            bag_name = query['bag'][0]
            tiddler_title = query['tiddler'][0]
        except KeyError:
            raise HTTP400('bad query: bag and tiddler required')

        if not (bag_name and tiddler_title):
            raise HTTP400('bad query: bag and tiddler required')

        bag = Bag(bag_name)
        try:
            bag = store.get(bag)
            bag = augment_bag(store, bag)
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
        'socket_link': config.get('socket.link'),
        'csrf_token': get_nonce(environ),
        'gravatar': gravatar(environ),
        'bag': bag,
        'message': message,
        'user': usersign['name'],
        'tiddler': tiddler,
        'etag': tiddler_etag(environ, tiddler).replace('"',
            '').split(':', 1)[0]
    })
