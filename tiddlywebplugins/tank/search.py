"""
Routines associated with finding and listing tags.

An experiment for now.
"""

import re

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.policy import PermissionsError
from tiddlywebplugins.whoosher import get_searcher, query_parse

QUERY_PARSE_RE = re.compile(r'(\w+):("[^"]+")\s*')


def list_tags(environ, start_response):
    """
    Plain text list of tags in a certain context.

    If a q query parameter is provided, then that is used to limit
    the search space for tags. For example q=modifier:cdent bag:foobar
    would return tags only from tiddlers in the bag foobar with most
    recent modifier of cdent.
    """
    config = environ['tiddlyweb.config']
    query = environ['tiddlyweb.query'].get('q', [None])[0]

    searcher = get_searcher(config)

    if query:
        # This parsing means that the if there are of the same keyword
        # the last one wins. This is okay because using both would
        # be illogical.
        kwargs = {}
        for match in QUERY_PARSE_RE.finditer(query):
            kwargs[match.group(1)] = match.group(2)
        documents = searcher.documents(**kwargs)
    else:
        documents = searcher.documents()

    # As yet unknown if this will be slow or not.
    set_tags = set()
    for stored_fields in documents:
        set_tags.update(stored_fields['tags'].split(','))

    start_response('200 OK', [('Content-Type', 'text/plain; charset=UTF-8')])

    return '\n'.join(set_tags)


def get_comp_bags(store, config, usersign):
    """
    Saving for later. Return a list of bags that can be used in
    comps.
    """
    comp_bags = []
    for result in full_search(config, 'title:app'):
        bag, _ = result['id'].split(':', 1)
        bag = store.get(Bag(bag))
        try:
            bag.policy.allows(usersign, 'read')
            comp_bags.append(bag)
        except PermissionsError:
            pass
    return comp_bags


def full_search(config, query):
    query = query_parse(config, query)
    searcher = get_searcher(config)
    return searcher.search(query)
