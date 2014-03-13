"""
Closet is a binary store.
"""
from wsgi_intercept import requests_intercept
import wsgi_intercept

import requests
import shutil

from tiddlyweb.web.serve import load_app
from tiddlyweb.config import config
from tiddlyweb.store import StoreError
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.user import User

from tiddlywebplugins.utils import get_store

from .fixtures import establish_user_auth


def setup_module(module):
    try:
        shutil.rmtree('indexdir')
        shutil.rmtree('store')
    except:
        pass
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

    test_bag1.policy.accept = ['NONE']
    store.put(test_bag1)
    module.environ = {'tiddlyweb.store': store, 'tiddlyweb.config': config}
    module.store = store
    module.cookie, module.csrf = establish_user_auth(config, store,
            'tankt.peermore.com:8080', 'tester')


def test_post_to_closet():
    url = 'http://tankt.peermore.com:8080/closet/newtank'
    data = {'csrf_token': csrf, 'redir': 1}
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
    requests_intercept.install()


def test_post_non_binary():
    url = 'http://tankt.peermore.com:8080/closet/newtank'
    data = {'csrf_token': csrf, 'redir': 1}
    files = {'file': ('foo.text', '# some text\n', 'text/x-plain')}
    headers = {'cookie': cookie}
    response = requests.post(url, data=data, files=files, headers=headers,
            allow_redirects=False)

    assert response.status_code == 303
    assert response.headers['location'] == 'http://tankt.peermore.com:8080/bags/newtank/tiddlers/foo.text'

    response = requests.get(response.headers['location'], allow_redirects=False)
    assert response.status_code == 200
    assert response.headers['content-type'].startswith('text/x-plain')
    assert '# some text' in response.text


def test_valiator_to_s3():
    url = 'http://tankt.peermore.com:8080/bags/newtank/tiddlers/somestuff'
    data = open('test/heg3.gif', 'rb').read()
    headers = {'content-type': 'image/gif'}
    response = requests.put(url, data=data, headers=headers)

    assert response.status_code == 204
    location = response.headers['location']
    assert location == 'http://tankt.peermore.com:8080/bags/newtank/tiddlers/somestuff'

    response = requests.get(location, allow_redirects=False)

    assert response.status_code == 302
    location = response.headers['location']
    assert location.startswith('https://tank-binaries.s3')
