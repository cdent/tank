"""
Stubbing in the stubs.
"""

from tiddlyweb.store import NoBagError
from tiddlyweb.util import merge_config, binary_tiddler
from tiddlyweb.web.validator import (BAG_VALIDATORS, TIDDLER_VALIDATORS,
        InvalidBagError)

from tiddlywebplugins.atom import init as atom_init
from tiddlywebplugins.dispatcher import init as dispatcher_init
from tiddlywebplugins.dispatcher.listener import init as listener_init
from tiddlywebplugins.extraclude import init as extraclude_init
from tiddlywebplugins.links import init as links_init
from tiddlywebplugins.logout import init as logout_init
from tiddlywebplugins.oauth import init as oauth_init
from tiddlywebplugins.policyfilter import init as policy_init
from tiddlywebplugins.privateer import init as privateer_init
from tiddlywebplugins.whoosher import init as whoosh_init
from tiddlywebplugins.status import init as status_init

from tiddlywebplugins.csrf import CSRFProtector

from tiddlywebplugins.utils import replace_handler

# Simply importing enables the necessary code
import tiddlywebplugins.relativetime

from .config import config as tank_config
from .closet import closet, closet_binary
from .home import home, dash
from .tanks import list_tanks
from .register import register
from .wiki import wiki_page
from .forge import forge
from .edit import editor, edit
from .search import list_tags
from .composition import comp
from .auth import view_auth, make_key, destroy_key
from .policymgr import policymgr
from .httperror import PrettyError, raiser


SUBSCRIBER = 'SUBSCRIBER'


def establish_web(config):
    atom_init(config)
    extraclude_init(config)
    status_init(config)
    logout_init(config)
    oauth_init(config)
    privateer_init(config)

    selector = config['selector']
    if CSRFProtector not in config['server_request_filters']:
        config['server_request_filters'].append(CSRFProtector)
    if PrettyError not in config['server_response_filters']:
        config['server_response_filters'].insert(0, PrettyError)

    selector.status404 = raiser('404', 'path not found')
    selector.status405 = raiser('405', 'method not allow')

    replace_handler(selector, '/', dict(GET=home))
    selector.add('/auth/{key_name:segment}', DELETE=destroy_key)
    selector.add('/auth', GET=view_auth, POST=make_key)
    selector.add('/dash', GET=dash)
    selector.add('/register', POST=register)
    selector.add('/closet/{bag_name:segment}', POST=closet)
    selector.add('/tanks', GET=list_tanks)
    selector.add('/tanks/{bag_name:segment}[/{tiddler_name:segment}]',
            GET=wiki_page)
    selector.add('/edit', GET=editor, POST=edit)
    selector.add('/forge', POST=forge)
    selector.add('/tags', GET=list_tags)
    selector.add('/comps/{recipe_name:segment}', GET=comp)
    selector.add('/policymgr', GET=policymgr)


def bag_quota(bag, environ):
    """
    Check to see if more bags are allowed for the current user.
    """
    store = environ['tiddlyweb.store']
    config = environ['tiddlyweb.config']
    usersign = environ['tiddlyweb.usersign']
    username = usersign['name']
    user_roles = usersign['roles']
    max_bags = config.get('tank.bag_limit', 5)

    if SUBSCRIBER in user_roles:
        return

    bag_names = [stored_bag.name for stored_bag
            in _bags_for_user(store, username)]

    if bag.name in bag_names:
        return
    if len(bag_names) >= max_bags:
        raise InvalidBagError('bag limit reached')


def _bags_for_user(store, username):
    def load_and_test_bag(bag):
        try:
            bag = store.get(bag)
        except NoBagError:
            return False
        return bag.policy.owner == username and not bag.name.startswith('_')

    return (bag for bag in store.list_bags() if load_and_test_bag(bag))


def binary_trap(tiddler, environ):
    if binary_tiddler(tiddler):
        tiddler = closet_binary(environ, tiddler)


def make_validators():
    BAG_VALIDATORS.append(bag_quota)
    TIDDLER_VALIDATORS.append(binary_trap)


def init(config):
    merge_config(config, tank_config, reconfig=True)
    whoosh_init(config)
    links_init(config)
    policy_init(config)
    dispatcher_init(config)
    listener_init(config)
    if 'selector' in config:
        make_validators()
        establish_web(config)
    # second time to ensure serializers are correct
    merge_config(config, tank_config, reconfig=True)
