"""
Test GETting editor and POSTing edits.

Simple for now, ignoring auth.
"""

from wsgi_intercept import httplib2_intercept
import wsgi_intercept

import shutil
import httplib2
import urllib


from tiddlyweb.web.serve import load_app
from tiddlyweb.config import config
from tiddlyweb.store import StoreError
from tiddlyweb.model.bag import Bag

from tiddlywebplugins.utils import get_store


def setup_module(module):
    try:
        shutil.rmtree('indexdir')
        shutil.rmtree('store')
    except:
        pass

    app = load_app()

    def app_fn(): return app

    httplib2_intercept.install()
    wsgi_intercept.add_wsgi_intercept('tankt.peermore.com', 8080, app_fn)

    store = get_store(config)
    test_bag = Bag('editable')

    try:
        store.delete(test_bag)
    except StoreError:
        pass

    store.put(test_bag)
    module.environ = {'tiddlyweb.store': store, 'tiddlyweb.config': config}
    module.store = store
    module.http = httplib2.Http()
    module.csrf = None


def test_get_editor():
    response, content = http.request(
            'http://tankt.peermore.com:8080/edit?bag=editable;tiddler=index')

    assert response['status'] == '200'
    assert response['content-type'].lower() == 'text/html; charset=utf-8'

    assert '<button><a href="/tanks/editable/index">Cancel Edit</a></button>' in content

    csrf = content.split('"csrf_token" value="')[1].split('"')[0]


def test_post_edit():
    data = {
        'bag': 'editable',
        'title': 'index',
        'text': '# oh hi\n',
        'type': 'text/x-markdown',
        'tags': '',
        'csrf_token': csrf,
        #'etag': 'editable/index/0',
    }

    response, content = http.request(
            'http://tankt.peermore.com:8080/edit',
            method='POST',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            body=urllib.urlencode(data))

    assert response['status'] == '400'
    assert "bad query: incomplete form, 'etag'" in content

    data['etag'] = 'editable/index/0'

    response, content = http.request(
            'http://tankt.peermore.com:8080/edit',
            method='POST',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            body=urllib.urlencode(data))

    assert response['status'] == '200'
    assert '<h1 id="oh-hi">oh hi</h1>' in content
