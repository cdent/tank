"""
Various utils that need a home.
"""


from tiddlyweb.control import filter_tiddlers
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.policy import PermissionsError
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.store import NoBagError
from tiddlyweb.util import renderable
from tiddlyweb.web.util import encode_name, server_base_url

from tiddlywebplugins.links.linksmanager import LinksManager

from .policy import determine_tank_type, POLICY_ICONS
from .search import get_tiddlers_from_search


INDEX_PAGE = 'index'


def augment_bag(store, bag, username=None):
    """
    Augment a bag object with information about it's policy type.
    """
    if not bag.store:
        bag = store.get(bag)
    if not username:
        username = bag.policy.owner
    policy_type = determine_tank_type(bag, username)
    bag.icon = POLICY_ICONS[policy_type]
    bag.type = policy_type
    return bag


def tank_uri(environ, tank_name, slash=False):
    """
    Create a redirect URI for a given tank.
    """
    return server_base_url(environ) + '/tanks/%s' % encode_name(tank_name)


def tank_page_uri(environ, tank_name, tiddler_title):
    """
    Create a redirect URI for a given page/tiddler within a tank.
    """
    return tank_uri(environ, tank_name) + '/%s' % encode_name(tiddler_title)


def tank_tiddler_uri(environ, tiddler):
    """
    Create a uri for a given tank page based on a tiddler object.
    """
    return tank_page_uri(environ, tiddler.bag, tiddler.title)


def tank_tiddler_resolver(environ, target, tiddler):
    """
    Modify a tiddler object to add a bag of the tank named by target.

    Check permissions and let Store and Permission errors raise.
    """
    store = environ['tiddlyweb.store']
    bag = Bag(target)
    bag = store.get(bag)
    bag.policy.allows(environ['tiddlyweb.usersign'], 'read')
    tiddler.bag = target


def get_sisterlinks(environ, tiddler):
    """
    Find other tiddlers on the service with the title of this one.
    """
    return get_tiddlers_from_search(environ, 'title:%s' % tiddler.title)


def get_backlinks(environ, tiddler):
    """
    Extract the current backlinks for this tiddler.
    """
    store = environ['tiddlyweb.store']
    usersign = environ['tiddlyweb.usersign']

    links_manager = LinksManager(environ)
    links = links_manager.read_backlinks(tiddler)
    back_tiddlers = []

    for link in links:
        container, title = link.split(':', 1)
        tiddler = Tiddler(title, container)
        if _is_readable(store, usersign, tiddler):
            back_tiddlers.append(tiddler)

    return back_tiddlers


def get_rellinks(environ, tiddler):
    """
    Create a dict of rellinks for this tiddler in this tank.
    """
    store = environ['tiddlyweb.store']
    bag_name = tiddler.bag
    links = {'index': True}
    if tiddler.title == INDEX_PAGE:
        links['index'] = False

    tiddlers = [filtered_tiddler.title for filtered_tiddler in
            filter_tiddlers(store.list_bag_tiddlers(Bag(bag_name)),
                'sort=modified', environ)
            if renderable(store.get(filtered_tiddler), environ)]

    try:
        this_index = tiddlers.index(tiddler.title)
        prev_index = this_index - 1
        if prev_index >= 0:
            prev_tiddler = tiddlers[prev_index]
        else:
            prev_tiddler = None
        try:
            next_tiddler = tiddlers[this_index + 1]
        except IndexError:
            next_tiddler = None

        links['prev'] = prev_tiddler
        links['next'] = next_tiddler
    except ValueError:
        pass

    return links

def _is_readable(store, usersign, tiddler):
    try:
        bag = store.get(Bag(tiddler.bag))
        bag.policy.allows(usersign, 'read')
        return True
    except (NoBagError, PermissionsError):
        return False
