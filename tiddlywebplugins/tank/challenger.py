"""
Challenger that pushes folk to github.
"""

import logging

from tiddlyweb.web.challengers import ChallengerInterface

from .templates import send_template
from .util import get_auth_server_info


LOGGER = logging.getLogger(__name__)


class Challenger(ChallengerInterface):
    """
    Present a link to GitHub auth.
    """

    desc = "Auth via OAuth"

    def challenge_get(self, environ, start_response):
        """
        Respond to a ``GET`` with a link.
        """
        try:
            redirect = environ['tiddlyweb.query']['tiddlyweb_redirect'][0]
        except KeyError:
            redirect = None

        auth_server_info = get_auth_server_info(environ)

        start_response('200 OK', [('Content-Type',
            'text/html; charset=UTF-8')])

        return send_template(environ, 'challenger.html', {
            'redirect': redirect,
            'auth_server_info': auth_server_info
        })
