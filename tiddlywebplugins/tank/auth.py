"""
View and make Auth token keys.
"""

from httpexceptor import HTTP404, HTTP409

from tiddlywebplugins.oauth.provider import make_access_token
from tiddlywebplugins.templates import get_template
from tiddlywebplugins.utils import require_any_user

from tiddlyweb.control import filter_tiddlers
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.serializer import Serializer
from tiddlyweb.store import NoTiddlerError
from tiddlyweb.web.util import get_route_value

from .home import gravatar
from .csrf import get_nonce


AUTH_TEMPLATE = 'auth.html'


@require_any_user()
def view_auth(environ, start_response):
    """
    Get a list of extant keys with an interface
    to revoke and to create more.
    """
    config = environ['tiddlyweb.config']
    store = environ['tiddlyweb.store']
    usersign = environ['tiddlyweb.usersign']
    username = usersign['name']
    bag_name = config.get('oauth.tokens_bag', 'oauth_tokens')

    our_tokens = [store.get(tiddler) for tiddler in
            filter_tiddlers(store.list_bag_tiddlers(Bag(bag_name)),
                'select=modifier:%s' % username, environ)]

    template = get_template(environ, AUTH_TEMPLATE)
    start_response('200 OK', [
        ('Content-Type', 'text/html; charset=UTF-8'),
        ('Cache-Control', 'no-cache')])
    return template.generate({
        'socket_link': config.get('socket.link'),
        'csrf_token': get_nonce(environ),
        'gravatar': gravatar(environ),
        'user': username,
        'tokens': our_tokens,
    })


@require_any_user()
def make_key(environ, start_response):
    """
    Create a new key (as a tiddler).
    """
    store = environ['tiddlyweb.store']
    query = environ['tiddlyweb.query']
    desc = query.get('desc', [''])[0]
    username = environ['tiddlyweb.usersign']['name']
    client = get_client(environ)

    token = make_access_token(environ, username, client)
    token.text = desc
    store.put(token)

    serializer = Serializer('json', environ)
    serializer.object = token
    content = serializer.to_string()

    start_response('200 OK', [
        ('Content-Type', 'application/json')])
    return [content]


def get_client(environ):
    return 'us'


@require_any_user()
def destroy_key(environ, start_response):
    """
    Remove a key.
    """
    config = environ['tiddlyweb.config']
    store = environ['tiddlyweb.store']
    username = environ['tiddlyweb.usersign']['name']
    bag_name = config.get('oauth.tokens_bag', 'oauth_tokens')
    key_name = get_route_value(environ, 'key_name')

    tiddler = Tiddler(key_name, bag_name)
    try:
        tiddler = store.get(tiddler)
    except NoTiddlerError:
        raise HTTP404('key does not exist')

    if tiddler.modifier != username:
        raise HTTP409('owner mismatch')

    store.delete(tiddler)

    start_response('204 No Content', [
        ('Content-Type', 'text/plain')])

    return []
