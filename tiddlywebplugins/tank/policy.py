
from tiddlyweb.model.policy import Policy

def private_policy(username):
    return Policy(owner=username,
            read=[username],
            write=[username],
            create=[username],
            delete=[username],
            manage=[username],
            accept=['NONE'])


def protected_policy(username):
    return Policy(owner=username,
            read=[],
            write=[username],
            create=[username],
            delete=[username],
            manage=[username],
            accept=['NONE'])


def public_policy(username):
    return Policy(owner=username,
            read=[],
            write=[],
            create=[],
            delete=[],
            manage=[username],
            accept=['NONE'])


def determine_tank_type(tank, username):
    """
    Calculate what kind of policy this exiting tank has.
    """
    if tank.policy == private_policy(username):
        return 'private'
    if tank.policy == protected_policy(username):
        return 'protected'
    if tank.policy == public_policy(username):
        return 'public'
    return 'custom'


WIKI_MODES = {
    'private': private_policy,
    'protected': protected_policy,
    'public': public_policy,
}


POLICY_ICONS = {
    'private': 'fa-folder',
    'protected': 'fa-folder-o',
    'public': 'fa-folder-open-o',
    'custom': 'fa-wrench',
}
