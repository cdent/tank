"""
Test validation routines.
"""

import pytest
import shutil

from tiddlyweb.config import config
from tiddlyweb.web.validator import validate_bag, InvalidBagError
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.user import User

from tiddlywebplugins.utils import get_store
from tiddlywebplugins.tank import init, SUBSCRIBER


def setup_module(module):
    try:
        shutil.rmtree('store')
    except:
        pass
    init(config)
    module.store = get_store(config)
    module.environ = {
        'tiddlyweb.config': config,
        'tiddlyweb.store': module.store,
        'tiddlyweb.usersign': {
            'name': 'cdent',
            'roles': ['MEMBER']
        }
    }


def test_bag_validator():
    config['tank.bag_limit'] = 1

    bag = Bag('bagone')
    bag.policy.owner = 'cdent'
    validate_bag(bag, environ)
    store.put(bag)

    bag = Bag('bagtwo')
    bag.policy.owner = 'cdent'
    with pytest.raises(InvalidBagError):
        validate_bag(bag, environ)

    environ['tiddlyweb.usersign']['roles'].append(SUBSCRIBER)

    bag = Bag('bagtwo')
    bag.policy.owner = 'cdent'
    validate_bag(bag, environ)
    store.put(bag)

    bag = store.get(Bag('bagtwo'))
    assert bag.name == 'bagtwo'
