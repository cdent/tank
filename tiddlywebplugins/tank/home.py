"""
Home or Frontpage of Tank.

If GUEST, shiny make you want it.
If logged in, your home page/dashboard.
"""

from hashlib import md5

from tiddlyweb.store import StoreError

from tiddlywebplugins.templates import get_template
from tiddlywebplugins.utils import require_any_user

from tiddlywebplugins.whoosher import query_parse, get_searcher

from .policy import determine_tank_type, POLICY_ICONS
from .search import get_comp_bags


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

    frontpage_template = get_template(environ, FRONTPAGE_TEMPLATE)
    start_response('200 OK', [
        ('Content-Type', 'text/html; charset=UTF-8'),
        ('Cache-Control', 'no-cache')])
    return frontpage_template.generate({'user': username})


@require_any_user()
def dash(environ, start_response, message=None):
    """
    Display info for the current user.
    """
    usersign = environ['tiddlyweb.usersign']
    username = usersign['name']
    store = environ['tiddlyweb.store']
    config = environ['tiddlyweb.config']

    def load_and_test_entity(entity):
        try:
            entity = store.get(entity)
        except StoreError:
            return False
        return entity.policy.owner == username and not entity.name.startswith('_')

    def augment_bag(bag):
        bag = store.get(bag)
        policy_type = determine_tank_type(bag, username)
        bag.icon = POLICY_ICONS[policy_type]
        bag.type = policy_type
        return bag

    kept_bags = (augment_bag(bag) for bag in store.list_bags()
            if load_and_test_entity(bag))

    comp_bags = get_comp_bags(store, config, usersign)

    comps = (recipe for recipe in store.list_recipes()
            if load_and_test_entity(recipe))

    dash_template = get_template(environ, DASH_TEMPLATE)
    start_response('200 OK', [
        ('Content-Type', 'text/html; charset=UTF-8'),
        ('Cache-Control', 'no-cache')])
    return dash_template.generate({
        'gravatar': gravatar(environ),
        'user': username,
        'bags': kept_bags,
        'message': message,
        'comp_bags': comp_bags,
        'comps': comps,
    })
