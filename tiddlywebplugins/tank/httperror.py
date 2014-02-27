"""
Handle 4xx errrors.

Based on https://github.com/FND/tiddlywebplugins.bfw/pull/6
"""

from httpexceptor import HTTPException, HTTP404

from tiddlywebplugins.templates import get_template


ERROR_TEMPLATE = '4xx.html'


class PrettyError(object):
    """
    Trap 4xx errors and temlpatize.
    """

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response, exc_info=None):
        try:
            return self.application(environ, start_response)
        except HTTPException as exc:
            if exc.status.startswith('4'):
                return send_error(environ, start_response, exc)
            else:
                raise


def send_error(environ, start_response, exc, allow=None):
    error = {
        'status': exc.status,
        'message': exc.message
    }

    template = get_template(environ, ERROR_TEMPLATE)
    headers = [
            ('Content-type', 'text/html; charset=utf-8')]
    if allow:
        headers.append(('Allow', allow))
    start_response(exc.status, headers)

    data = {'error': error}
    return template.generate(data)


def method_not_allowed(environ, start_response, exc=None):
    """
    Package up special format method not allowed.
    """
    allow = ', '.join(environ['selector.methods'])
    exc = HTTPException('The method specified in the Request-Line '
        'is not allowed for the resource identified by the Request-URI.')
    exc.status = '405 Method Not Allowed'
    return send_error(environ, start_response, exc, allow=allow)


def raiser(status, message):
    """
    Return functions to raise a 404 or 405 with a message.
    """
    def cause404(environ, start_response):
        raise HTTP404(message)
    if status == '404':
        return cause404
    if status == '405':
        return method_not_allowed
    raise ValueError('attempt raise invalid raiser')
