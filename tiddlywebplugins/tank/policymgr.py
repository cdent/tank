"""
Present a SPA for managing policies on stuff.
"""

from tiddlywebplugins.templates import get_template
from tiddlywebplugins.utils import require_any_user

from .home import gravatar

POLICYMGR_TEMPLATE = 'policymgr.html'

@require_any_user()
def policymgr(environ, start_response):
    config = environ['tiddlyweb.config']
    usersign = environ['tiddlyweb.usersign']
    template = get_template(environ, POLICYMGR_TEMPLATE)
    start_response('200 OK', [
        ('Content-Type', 'text/html; charset=UTF-8')])
    return template.generate({
        'socket_link': config.get('socket.link'),
        'gravatar': gravatar(environ),
        'user': usersign['name'],
    })
