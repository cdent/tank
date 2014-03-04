"""
Home or Frontpage of Tank.

If GUEST, shiny make you want it.
If logged in, your home page/dashboard.
"""

from tiddlyweb.filters import recursive_filter, parse_for_filters
from tiddlyweb.store import StoreError

from tiddlywebplugins.utils import require_any_user

from .search import get_comp_bags
from .templates import send_template
from .util import augment_bag


DASH_TEMPLATE = 'dash.html'
FRONTPAGE_TEMPLATE = 'frontpage.html'
#FRONTPAGE_CACHE_TIME = 300  # XXX caching a bit too aggressive


def home(environ, start_response):
    """
    Display a starting page.
    """
    start_response('200 OK', [
        ('Content-Type', 'text/html; charset=UTF-8'),
        ('Cache-Control', 'no-cache')])

    return send_template(environ, FRONTPAGE_TEMPLATE)


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

    start_response('200 OK', [
        ('Content-Type', 'text/html; charset=UTF-8'),
        ('Cache-Control', 'no-cache')])
    return send_template(environ, DASH_TEMPLATE, {
        'owned_bags': owned_bags,
        'friendly_bags': friendly_bags,
        'message': message,
        'comp_bags': comp_bags,
        'owned_comps': owned_comps,
    })


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
