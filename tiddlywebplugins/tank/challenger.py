"""
Challenger that pushes folk to github.
"""

import logging

from tiddlyweb.web.challengers import ChallengerInterface

from tiddlywebplugins.templates import get_template


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
        template = get_template(environ, 'challenger.html')
        start_response('200 OK', [('Content-Type',
            'text/html; charset=UTF-8')])

        return template.generate()
