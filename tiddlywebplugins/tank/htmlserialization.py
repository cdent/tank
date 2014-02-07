"""
Override the default HTML Serialization so that search
results go through the existing tank template structure
and links are to tiddlers in their tank, not in their bag.
"""

from tiddlywebplugins.atom.htmllinks import Serialization as HTMLSerialization

from tiddlywebplugins.templates import get_template

from .home import gravatar


SEARCH_TEMPLATE = 'search.html'


class Serialization(HTMLSerialization):

    def list_tiddlers(self, tiddlers):
        if not tiddlers.is_search:
            return HTMLSerialization.list_tiddlers(self, tiddlers)

        tiddlers.link = '/search?%s' % self.environ.get('QUERY_STRING', '')

        search_template = get_template(self.environ, SEARCH_TEMPLATE)
        return search_template.generate({
            'gravatar': gravatar(self.environ),
            'user': self.environ['tiddlyweb.usersign']['name'],
            'tiddlers': tiddlers
        })
