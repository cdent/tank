"""
Home or Frontpage of Tank.

If GUEST, shiny make you want it.
If logged in, your home page/dashboard.
"""

from hashlib import md5

from tiddlyweb.filters import recursive_filter, parse_for_filters
from tiddlyweb.store import StoreError

from tiddlywebplugins.templates import get_template
from tiddlywebplugins.utils import require_any_user

from tiddlywebplugins.whoosher import query_parse, get_searcher

from .policy import determine_tank_type, POLICY_ICONS
from .search import get_comp_bags
from .csrf import get_nonce


GRAVATAR = 'https://www.gravatar.com/avatar/%s'
DASH_TEMPLATE = 'dash.html'
FRONTPAGE_TEMPLATE = 'frontpage.html'
#FRONTPAGE_CACHE_TIME = 300  # XXX caching a bit too aggressive


def gravatar(environ):
    """
    Generate a gravatar link.
    """
    email = environ.get('tank.user_info', {}).get('email', '')
    return GRAVATAR % md5(email.lower()).hexdigest()


def home(environ, start_response):
    """
    Display a starting page.
    """
    username = environ['tiddlyweb.usersign']['name']
    config = environ['tiddlyweb.config']

    frontpage_template = get_template(environ, FRONTPAGE_TEMPLATE)
    start_response('200 OK', [
        ('Content-Type', 'text/html; charset=UTF-8'),
        ('Cache-Control', 'no-cache')])
    return frontpage_template.generate({
        'user': username,
        'socket_link': config.get('socket.link'),
    })


@require_any_user()
def dash(environ, start_response, message=None):
    """
    Display info for the current user.
    """
    usersign = environ['tiddlyweb.usersign']
    username = usersign['name']
    store = environ['tiddlyweb.store']
    config = environ['tiddlyweb.config']

    owned_bags = get_owned_bags(store, username)
    owned_comps = get_owned_comps(store, username)
    comp_bags = get_comp_bags(store, config, usersign)
    friendly_bags = get_friendly_bags(store, environ, username)

    dash_template = get_template(environ, DASH_TEMPLATE)
    start_response('200 OK', [
        ('Content-Type', 'text/html; charset=UTF-8'),
        ('Cache-Control', 'no-cache')])
    return dash_template.generate({
        'socket_link': config.get('socket.link'),
        'gravatar': gravatar(environ),
        'user': username,
        'owned_bags': owned_bags,
        'friendly_bags': friendly_bags,
        'message': message,
        'comp_bags': comp_bags,
        'owned_comps': owned_comps,
        'csrf_token': get_nonce(environ)
    })


def augment_bag(store, bag, username=None):
    """
    Augment a bag object with information about it's policy type.
    """
    bag = store.get(bag)
    if not username:
        username = bag.policy.owner
    policy_type = determine_tank_type(bag, username)
    bag.icon = POLICY_ICONS[policy_type]
    bag.type = policy_type
    return bag


def load_and_test_entity(store, entity, username, negate_user=False):
    try:
        entity = store.get(entity)
    except StoreError:
        return False
    if negate_user:
        return (entity.policy.owner != username
                and not entity.name.startswith('_'))
    return (entity.policy.owner == username
            and not entity.name.startswith('_'))


def get_friendly_bags(store, environ, username):
    """
    Return a list of bags that this user can write in.
    """
    def filter(environ, filter_string, entities):
        return recursive_filter(parse_for_filters(
            filter_string, environ)[0], entities)

    return (augment_bag(store, bag) for bag in
            filter(environ, 'select=policy:create', store.list_bags())
            if load_and_test_entity(store, bag, username, negate_user=True))


def get_owned_bags(store, username):
    """
    Return a list of bags owned by username, except for ones
    that have a name starting with '_'.
    """
    return (augment_bag(store, bag) for bag in store.list_bags()
            if load_and_test_entity(store, bag, username))


def get_owned_comps(store, username):
    """
    Return a list of comps owned by username, except for ones
    that have a name starting with '_'.
    """
    return (recipe for recipe in store.list_recipes()
            if load_and_test_entity(store, recipe, username))
