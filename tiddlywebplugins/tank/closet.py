"""
POST binaries to alternate storage, create a canonical uri tiddler
pointing to that storage.
"""

import os

from httpexceptor import HTTP400, HTTP404
from uuid import uuid4
from mimetypes import guess_extension, guess_type

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.web.util import get_route_value, tiddler_url, server_base_url
from tiddlywebplugins.utils import require_role


@require_role('MEMBER')
def closet(environ, start_response):
    """
    Read file input and write it to special storage.
    """
    store = environ['tiddlyweb.store']
    usersign = environ['tiddlyweb.usersign']
    bag_name = get_route_value(environ, 'bag_name')

    bag = store.get(Bag(bag_name))

    bag.policy.allows(usersign, 'create')
    bag.policy.allows(usersign, 'write')

    files = environ['tiddlyweb.input_files']

    if not files:
        raise HTTP400('missing file input')

    tiddlers = []
    for input_file in files:
        filename = input_file.filename
        binary_storage = BinaryDisk(environ, input_file)
        url = binary_storage.store()
        tiddler = Tiddler(filename, bag_name)
        tiddler.fields['_canonical_uri'] = url
        tiddler.modifier = usersign['name']
        tiddler.type = input_file.type
        store.put(tiddler)
        tiddlers.append(tiddler)

    start_response('303 See Other', [
        ('Location', tiddler_url(environ, tiddlers[-1]))])
    return []


def closet_item(environ, start_response):
    file_name = get_route_value(environ, 'file_name')

    file_target = os.path.join(BinaryDisk.Disk, file_name)
    mime_type = guess_type(file_name)[0] or 'application/octet-stream'

    if not os.path.exists(file_target):
        raise HTTP404('file not found')

    start_response('200 OK', [
        ('Content-Type', mime_type)])
    content = open(file_target, 'rb')
    if 'wsgi.file_wrapper' in environ:
        print 'using wrapper'
        return environ['wsgi.file_wrapper'](content)
    else:
        return iter(lambda: content.read(4096), '')


class BinaryDisk(object):

    Disk = 'closet'

    def __init__(self, environ, filething):
        self.environ = environ
        self.filename = filething.name
        self.filehandle = filething.file
        self.extension = guess_extension(filething.type) or ''
        self.targetname = uuid4().get_hex() + self.extension

    def store(self):
        with open(os.path.join(self.Disk, self.targetname),
                'wb') as diskfile:
            input_data = self.filehandle.read(4096)
            while input_data:
                diskfile.write(input_data)
                input_data = self.filehandle.read(4096)
            self.filehandle.close()
        return self._url()

    def _url(self):
        return server_base_url(self.environ) + '/closet/_/%s' % self.targetname
