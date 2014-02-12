"""
Produce csrf nonces for forms.
"""

from datetime import datetime

from tiddlywebplugins.csrf import get_nonce_components, gen_nonce


def get_nonce(environ):
    """
    Create a nonce that will last about an hour.
    """
    user, host, secret = get_nonce_components(environ)
    time = datetime.utcnow().strftime('%Y%m%d%H')
    return gen_nonce(user, host, time, secret)
