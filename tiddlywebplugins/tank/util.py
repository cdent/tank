"""
Various utils that need a home.
"""


from tiddlyweb.model.bag import Bag
from tiddlyweb.web.util import encode_name, server_base_url


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
