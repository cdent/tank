"""
Test creating a new tank via form.
"""
from wsgi_intercept import httplib2_intercept
import wsgi_intercept

import httplib2
import urllib


from tiddlyweb.web.serve import load_app
from tiddlyweb.config import config
from tiddlyweb.store import StoreError
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.user import User

from tiddlywebplugins.utils import get_store

from .fixtures import establish_user_auth


def setup_module(module):
    app = load_app()

    def app_fn(): return app

    httplib2_intercept.install()
    wsgi_intercept.add_wsgi_intercept('tankt.peermore.com', 8080, app_fn)

    store = get_store(config)
    test_bag1 = Bag('newtank')


    try:
        store.delete(test_bag1)
    except StoreError:
        pass


    module.environ = {'tiddlyweb.store': store, 'tiddlyweb.config': config}
    module.store = store
    module.http = httplib2.Http()
    module.cookie, module.csrf = establish_user_auth(config, store,
            'tankt.peermore.com:8080', 'tester')
    


def test_post_to_forge():
    data = {
        'name': 'newtank',
        'policy_type': 'protected',
        'csrf_token': csrf,
    }
    response, content = http.request('http://tankt.peermore.com:8080/forge',
            method='POST',
            headers={'Content-Type': 'application/x-www-form-urlencoded',
                'Cookie': cookie},
            body=urllib.urlencode(data))

    assert response['status'] == '200'
    assert '<link rel="edit" href="/bags/newtank/tiddlers/index">' in content
