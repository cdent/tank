"""
A composition is a recipe which results in tiddlers to
control the presentation of the tiddlers contained in the
tank.

Still working out the details of how this should work out.
"""

from httpexceptor import HTTP404

from tiddlyweb.control import determine_bag_from_recipe
from tiddlyweb.store import NoRecipeError, NoBagError
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.web.util import get_route_value
from tiddlyweb.web.handler.tiddler import _send_tiddler

def comp(environ, start_response):
    usersign = environ['tiddlyweb.usersign']
    store = environ['tiddlyweb.store']
    recipe_name = get_route_value(environ, 'recipe_name')

    tiddler = Tiddler('app')

    recipe = Recipe(recipe_name)
    try:
        recipe = store.get(recipe)
        recipe.policy.allows(usersign, 'read')
    except NoRecipeError as exc:
        raise HTTP404('unable to find recipe %s' % recipe_name)

    try:
        bag = determine_bag_from_recipe(recipe, tiddler, environ)
    except NoBagError as exc:
        raise HTTP404('%s not found via bag, %s' % (tiddler.title, exc))

    tiddler.bag = bag.name

    return _send_tiddler(environ, start_response, tiddler)
