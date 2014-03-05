"""
Closet is a binary store.
"""
from wsgi_intercept import requests_intercept
import wsgi_intercept

import requests

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

    requests_intercept.install()
    wsgi_intercept.add_wsgi_intercept('tankt.peermore.com', 8080, app_fn)

    store = get_store(config)
    test_bag1 = Bag('newtank')

    try:
        store.delete(test_bag1)
    except StoreError:
        pass

    store.put(test_bag1)
    module.environ = {'tiddlyweb.store': store, 'tiddlyweb.config': config}
    module.store = store
    module.cookie, module.csrf = establish_user_auth(config, store,
            'tankt.peermore.com:8080', 'tester')


def test_post_to_closet():
    url = 'http://tankt.peermore.com:8080/closet/newtank'
    data = {'csrf_token': csrf}
    files = {'file': ('heg3.gif', open('test/heg3.gif', 'rb'), 'image/gif')}
    headers = {'cookie': cookie}
    response = requests.post(url, data=data, files=files, headers=headers,
            allow_redirects=False)

    assert response.status_code == 303
    assert response.headers['location'] == 'http://tankt.peermore.com:8080/bags/newtank/tiddlers/heg3.gif'

    response = requests.get(response.headers['location'], allow_redirects=False)
    assert response.status_code == 302
    assert response.headers['location'].startswith(
            'https://tank-binaries.s3.amazonaws.com/')

    requests_intercept.uninstall()
    response = requests.get(response.headers['location'], allow_redirects=False)
    assert response.status_code == 200
    assert response.headers['content-type'] == 'image/gif'
