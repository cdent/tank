"""
Override the default HTML Serialization so that search
results go through the existing tank template structure
and links are to tiddlers in their tank, not in their bag.
"""

from tiddlywebplugins.atom.htmllinks import Serialization as HTMLSerialization

from .templates import send_template


SEARCH_TEMPLATE = 'search.html'


class Serialization(HTMLSerialization):

    def list_tiddlers(self, tiddlers):
        if not tiddlers.is_search:
            return HTMLSerialization.list_tiddlers(self, tiddlers)

        search_query = self.environ['tiddlyweb.query'].get('q', [''])[0]
        tiddlers.link = '/search?%s' % self.environ.get('QUERY_STRING', '')

        if 'bag:' in search_query and (
                'OR' not in search_query and 'AND' not in search_query):
            global_query = globalize_query(search_query)
        else:
            global_query = ''

        return send_template(self.environ, SEARCH_TEMPLATE, {
            'tiddlers': tiddlers,
            'global_query': global_query,
        })


def globalize_query(search_query):
    """
    Take the bag parts out of a search query.
    """
    query = ' '.join([part for part in search_query.split()
        if not part.startswith('bag:')])
    return query
