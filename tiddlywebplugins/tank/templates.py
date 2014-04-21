"""
Centralize some template handling code.

A lot of the same stuff is sent in the templates so may as well
keep it in one place.
"""

from hashlib import md5

from tiddlyweb.web.util import encode_name

from tiddlywebplugins.templates import get_template

from .csrf import get_nonce
from .util import tank_page_uri


DEFAULT_GRAVATAR = 'whitefish.png'
GRAVATAR = 'https://www.gravatar.com/avatar/%s?d=%s'


def gravatar(environ):
    """
    Generate a gravatar link.
    """
    email = environ.get('tank.user_info', {}).get('email', '')
    return GRAVATAR % (md5(email.lower()).hexdigest(),
            encode_name(tank_page_uri(environ, 'tank', DEFAULT_GRAVATAR)))


def send_template(environ, template_name, template_data=None):
    """
    Set some defualt data to send to template and then send it.
    """
    if template_data is None:
        template_data = {}

    config = environ.get('tiddlyweb.config', {})
    try:
        usersign = environ['tiddlyweb.usersign']
    except KeyError:
        usersign = {'name': 'GUEST', 'roles': []}
        environ['tiddlyweb.usersign'] = usersign

    template = get_template(environ, template_name)

    template_defaults = {
        'socket_link': config.get('socket.link'),
        'csrf_token': get_nonce(environ),
        'gravatar': gravatar(environ),
        'user': usersign['name'],
    }

    template_defaults.update(template_data)
    return template.generate(template_defaults)
