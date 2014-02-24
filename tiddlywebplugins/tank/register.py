"""
User registration handling.

We want to record more than the usual details about a user:

    * no password
    * an initial MEMBER role
    * and some JSON detail: email, full name, the date of signup
"""

import simplejson

from httpexceptor import HTTP400
from time import time

from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.user import User
from tiddlyweb.store import StoreError
from tiddlyweb.util import sha
from tiddlyweb.web.util import make_cookie, server_base_url

from tiddlywebplugins.utils import ensure_bag

from .wiki import create_wiki


DEFAULT_ROLE = 'MEMBER'
MAP_USER_POLICY = {
    'manage': ['NONE'],
    'read': ['NONE'],
    'write': ['NONE'],
    'create': ['NONE'],
    'delete': ['NONE']
}


def register(environ, start_response):
    """
    register the user
    """
    config = environ['tiddlyweb.config']
    store = environ['tiddlyweb.store']
    query = environ['tiddlyweb.query']
    try:
        server_name = query['server_name'][0]
        server_name_sig = query['server_name_sig'][0]
        server_login = query['server_login'][0]
        server_login_sig = query['server_login_sig'][0]
        username = query['login'][0]
        name = query['name'][0]
        email = query['email'][0]
        extra = query['extra'][0]
        redirect = query['redirect'][0]
    except (KeyError, ValueError) as exc:
        raise HTTP400('Incomplete form submission: %s' % exc)

    announcements = query.get('announcements', [None])[0]

    # Bail out if some corrupted the form input.
    secret = config['secret']
    name_sig = sha('%s%s' % (server_name, secret)).hexdigest() 
    login_sig = sha('%s%s' % (server_login, secret)).hexdigest()
    if name_sig != server_name_sig or login_sig != server_login_sig:
        raise HTTP400('Invalid request')

    user = User(username)
    try:
        store.get(user)
        raise HTTP400('That username is not available.')
    except StoreError:  # we expect and want this
        pass

    user.add_role(DEFAULT_ROLE)
    user.note = simplejson.dumps({
        'registered': time(),
        'name': name,
        'email': email,
        'extra': extra,
        'announcements': announcements is not None
    })

    map_bag_name = config.get('magicuser.map', 'MAPUSER')
    ensure_bag(map_bag_name, store, policy_dict=MAP_USER_POLICY)
    tiddler = Tiddler(server_login, map_bag_name)
    try:
        store.get(tiddler)
        raise HTTP400('That remote user is already mapped')
    except StoreError:
        pass
    tiddler.fields['mapped_user'] = username

    store.put(tiddler)
    store.put(user)

    create_wiki(environ, '_%s-data' % username, mode='private',
            username=username, desc='Data Files', validate=False)
    create_wiki(environ, '%s-notebook' % username, mode='private',
            username=username, desc='Private Notebook', validate=False)
    create_wiki(environ, '%s' % username, mode='protected',
            username=username, desc='Share Stuff', validate=False)

    redirect_uri = '%s%s' % (server_base_url(environ), redirect)
    secret = config['secret']
    cookie_age = config.get('cookie_age', None)
    cookie_header_string = make_cookie('tiddlyweb_user', server_login,
            mac_key=secret, path='/', expires=cookie_age)
    start_response('303 See Other',
            [('Set-Cookie', cookie_header_string),
                ('Content-Type', 'text/plain'),
                ('Location', str(redirect_uri))])
    return [redirect_uri]
