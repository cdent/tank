"""
Present a list of tanks readable by the current user.
"""

from tiddlyweb.filters import recursive_filter, parse_for_filters


from .templates import send_template
from .util import augment_bag


TANK_LIST_TEMPLATE = 'tanks.html'


def list_tanks(environ, start_response):
    """
    Filter all the available bags for read, and show em.
    """
    store = environ['tiddlyweb.store']

    bags = get_readable_bags(store, environ)

    start_response('200 OK', [
        ('Content-Type', 'text/html; charset=utf-8')])

    return send_template(environ, TANK_LIST_TEMPLATE, {'bags': bags})


def get_readable_bags(store, environ):
    """
    Return a list of bags that this user can read.
    """
    def filter(environ, filter_string, entities):
        return recursive_filter(parse_for_filters(
            filter_string, environ)[0], entities)

    return (augment_bag(store, bag) for bag in
            filter(environ, 'select=policy:read;sort=name',
                store.list_bags()))
