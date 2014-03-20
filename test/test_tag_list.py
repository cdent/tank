"""
Test that we can get a reasonable list of tags from the
data source of /tags
"""

import shutil

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler

from tiddlyweb.config import config
from tiddlywebplugins.utils import get_store

from tiddlywebplugins.tank.search import get_indexed_tags
from tiddlywebplugins.tank import init


def setup_module(module):
    for dir in ('store', 'indexdir'):
        try:
            shutil.rmtree(dir)
        except:  # heavy!
            pass

    init(config)
    store = get_store(config)

    store.put(Bag('bagone'))
    store.put(Bag('bagtwo'))

    module.store = store


def test_for_tags():
    tiddler1 = Tiddler('one', 'bagone')
    tiddler2 = Tiddler('two', 'bagtwo')
    tiddler1.tags = ['alpha', 'beta']
    tiddler2.tags = ['alpha', 'gamma']
    store.put(tiddler1)
    store.put(tiddler2)

    tags = get_indexed_tags(config, None)

    assert len(tags) == 3
    assert sorted(tags) == ['alpha', 'beta', 'gamma']

    tags = get_indexed_tags(config, 'bag:"bagone"')
    assert len(tags) == 2
    assert sorted(tags) == ['alpha', 'beta']
