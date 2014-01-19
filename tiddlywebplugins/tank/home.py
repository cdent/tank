"""
Home or Frontpage of Tank.

If GUEST, shiny make you want it.
If logged in, your home page/dashboard.
"""

from tiddlywebplugins.templates import get_template
from tiddlywebplugins.utils import require_any_user


DASH_TEMPLATE = 'dash.html'
FRONTPAGE_TEMPLATE = 'frontpage.html'
#FRONTPAGE_CACHE_TIME = 300  # XXX caching a bit too aggressive


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
    username = environ['tiddlyweb.usersign']['name']
    store = environ['tiddlyweb.store']

    def load_and_test_bag(bag):
        try:
            bag = store.get(bag)
        except NoBagError:
            return False
        return bag.policy.owner == username and not bag.name.startswith('_')

    # XXX should add in metadata here about which are private
    kept_bags = (bag for bag in store.list_bags() if load_and_test_bag(bag))

    dash_template = get_template(environ, DASH_TEMPLATE)
    start_response('200 OK', [
        ('Content-Type', 'text/html; charset=UTF-8'),
        ('Cache-Control', 'no-cache')])
    return dash_template.generate({
        'user': username,
        'bags': kept_bags,
        'message': message
    })
