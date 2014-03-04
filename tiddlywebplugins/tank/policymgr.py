"""
Present a SPA for managing policies on stuff.
"""

from tiddlywebplugins.utils import require_any_user

from .templates import send_template

POLICYMGR_TEMPLATE = 'policymgr.html'


@require_any_user()
def policymgr(environ, start_response):
    start_response('200 OK', [
        ('Content-Type', 'text/html; charset=UTF-8')])
    return send_template(environ, POLICYMGR_TEMPLATE)
