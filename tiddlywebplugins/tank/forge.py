"""
Create a new tank.
"""

from httpexceptor import HTTP400

from tiddlyweb.model.bag import Bag
from tiddlyweb.store import NoBagError
from tiddlyweb.web.validator import validate_bag, InvalidBagError

from tiddlywebplugins.utils import require_role

from .policy import WIKI_MODES
from .util import tank_uri
from .home import dash


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
    usersign = environ['tiddlyweb.usersign']

    try:
        tank_name = query['name'][0]
        tank_policy = query['policy_type'][0]
    except KeyError:
        raise HTTP400('tank_name and tank_policy required')

    tank_desc = query.get('desc', [''])[0]

    try:
        create_wiki(environ, tank_name, mode=tank_policy,
                username=usersign['name'], desc=tank_desc)
    except InvalidBagError:
        return dash(environ, start_response, message='Over quota!')

    uri = tank_uri(environ, tank_name)
    start_response('303 See Other', [
        ('Location', str(uri))])
    return []
