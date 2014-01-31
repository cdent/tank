"""
Routines associated with finding and listing tags.

An experiment for now.
"""

from tiddlywebplugins.whoosher import get_searcher


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
        # XXX this is not robust in the face of wacky inputs
        # (including quoted inputs), for now we ride.
        kwargs = dict([entry.split(':') for entry in query.split()])
        documents = searcher.documents(**kwargs)
    else:
        documents = searcher.documents()

    # As yet unknown if this will be slow or not.
    set_tags = set()
    for stored_fields in documents:
        set_tags.update(stored_fields['tags'].split(','))

    start_response('200 OK', [('Content-Type', 'text/plain; charset=UTF-8')])

    return '\n'.join(set_tags)
