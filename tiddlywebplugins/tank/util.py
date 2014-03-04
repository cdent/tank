"""
Various utils that need a home.
"""


from tiddlyweb.control import filter_tiddlers
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.web.util import encode_name, server_base_url

from tiddlywebplugins.links.linksmanager import LinksManager


INDEX_PAGE = 'index'


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


def get_backlinks(environ, tiddler):
    """
    Extract the current backlinks for this tiddler.
    """
    store = environ['tiddlyweb.store']
    usersign = environ['tiddlyweb.usersign']

    links_manager = LinksManager(environ)
    links = links_manager.read_backlinks(tiddler)
    back_tiddlers = []

    def _is_readable(tiddler):
        try:
            bag = store.get(Bag(tiddler.bag))
            bag.policy.allows(usersign, 'read')
            return True
        except (NoBagError, PermissionsError):
            return False

    for link in links:
        container, title = link.split(':', 1)
        tiddler = Tiddler(title, container)
        if _is_readable(tiddler):
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
                'sort=modified', environ)]

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
