"""
API Key Extractor, based on the oauth extractor
but using a different header.
"""

from httpexceptor import HTTP401

from tiddlyweb.web.extractors import ExtractorInterface

from tiddlywebplugins.oauth.extractor import check_access_token


class Extractor(ExtractorInterface):
    """
    Look at the X-Tank-Key header for a token that
    looks like it might be oauth-ish and attempt to
    validate it.
    """

    def extract(self, environ, start_response):
        token = environ.get('HTTP_X_TANK_KEY', None)
        if token is None:
            return False

        # We have a token that might be oauth stuff,
        # so let's give it a go.
        candidate_username, scope = check_access_token(environ, token)

        if not candidate_username:
            raise HTTP401('invalid token')

        # XXX do something with scope eventually

        user = self.load_user(environ, candidate_username)
        return {"name": user.usersign, "roles": user.list_roles()}
