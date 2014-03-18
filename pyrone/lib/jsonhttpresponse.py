"""Module that contains special response type class: JSON response
"""

import logging

from pyramid.response import Response
from pyramid.httpexceptions import WSGIHTTPException
import json

from pyrone.lib import httpcode

HTTP_STATUSES = {
    httpcode.InternalServerError: '500 Internal Server Error',
    httpcode.BadRequest: '400 Bad Request',
    httpcode.NotFound: '404 Not Found',
    httpcode.Conflict: '409 Conflict'
}

log = logging.getLogger(__name__)

class JSONResponse(Response):
    def __init__(self, code=None, json_data=None, **kw):
        if json_data is None:
            json_data = ''

        if code in HTTP_STATUSES:
            status = HTTP_STATUSES[code]
        else:
            status = HTTP_STATUSES[httpcode.InternalServerError]
            json_data = {'error': 'JSONResponse: Unable to determine HTTP status code.'}

        Response.__init__(self, status=status, body=json.dumps(json_data),
            content_type='application/json', **kw)

        self.charset = 'utf-8'