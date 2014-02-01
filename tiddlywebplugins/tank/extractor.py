"""
An extractor that checks that the user extracted by the
wrapped extractor exists in the user store.
"""

import logging
import simplejson

from tiddlyweb.model.user import User
from tiddlyweb.store import StoreError
from tiddlyweb.web.extractors import ExtractorInterface


LOGGER = logging.getLogger(__name__)


class Extractor(ExtractorInterface):

    def extract(self, environ, start_response):
        config = environ['tiddlyweb.config']
        store = environ['tiddlyweb.store']

        wrapped_extractor = config.get('wrapped_extractor', 'simple_cookie')

        try:
            imported_module = __import__('tiddlyweb.web.extractors.%s' %
                   wrapped_extractor, {}, {}, ['Extractor'])
        except ImportError:
            try:
                imported_module = __import__(wrapped_extractor, {}, {},
                        ['Extractor'])
            except ImportError, exc:
                raise ImportError('could not load extractor %s: %s' %
                        (wrapped_extractor, exc))
        extractor = imported_module.Extractor()
        extracted_user = extractor.extract(environ, start_response)
        if extracted_user:
            LOGGER.debug('UserExtract:%s found %s', wrapped_extractor,
                    extracted_user)
            try:
                user = store.get(User(extracted_user['name']))
                environ['tank.user'] = user
                environ['tank.user_info'] = simplejson.loads(user.note)
                return extracted_user
            except StoreError:
                pass
        return False
