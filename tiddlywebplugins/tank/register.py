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

from tiddlyweb.model.user import User
from tiddlyweb.store import StoreError
from tiddlyweb.web.util import make_cookie, server_host_url


DEFAULT_ROLE = 'MEMBER'


def register(environ, start_response):
    """
    register the user
    """
    config = environ['tiddlyweb.config']
    store = environ['tiddlyweb.store']
    query = environ['tiddlyweb.query']
    try:
        username = query['login'][0]
        name = query['name'][0]
        email = query['email'][0]
        extra = query['extra'][0]
    except (KeyError, ValueError) as exc:
        raise HTTP400('Incomplete form submission: %s' % exc)

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
        'extra': extra
    })

    store.put(user)

    redirect_uri = '%sdash' % server_host_url(environ)
    secret = config['secret']
    cookie_age = config.get('cookie_age', None)
    cookie_header_string = make_cookie('tiddlyweb_user', user.usersign,
            mac_key=secret, path='/', expires=cookie_age)
    start_response('303 See Other', 
            [('Set-Cookie', cookie_header_string),
                ('Content-Type', 'text/plain'),
                ('Location', redirect_uri)])
    return [redirect_uri]
