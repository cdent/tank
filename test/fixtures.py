from datetime import datetime

from tiddlyweb.model.user import User
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.store import StoreError
from tiddlyweb.web.util import make_cookie

from tiddlywebplugins.utils import ensure_bag
from tiddlywebplugins.csrf import gen_nonce

def establish_user_auth(config, store, host, username):
    user = User(username)
    mapping_username = 'github-%s' % username
    mapping_tiddler = Tiddler(mapping_username, 'MAPUSER')
    mapping_tiddler.fields['mapped_user'] = username

    try:
        store.delete(user)
    except StoreError:
        pass
    try:
        store.delete(mapping_tiddler)
    except IOError:
        pass

    user.add_role('MEMBER')
    user.note = '{}'
    store.put(user)
    ensure_bag('MAPUSER', store)
    store.put(mapping_tiddler)
    stamp = datetime.utcnow().strftime('%Y%m%d%H')
    csrf = gen_nonce(username, host, stamp, config['secret'])
    cookie = make_cookie('tiddlyweb_user', mapping_username,
            mac_key=config['secret'], httponly=False)

    return cookie, csrf
