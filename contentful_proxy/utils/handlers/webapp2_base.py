# The MIT License (MIT)
# 
# Copyright (c) 2018 stanwood GmbH
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import json

import abc

import webapp2


class CustomBaseHandler(webapp2.RequestHandler):
    __metaclass__ = abc.ABCMeta

    def json_response(self, data, status=200):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.status_int = status
        self.response.write(json.dumps(data))


class CorsMixin(CustomBaseHandler):

    def dispatch(self):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        super(CorsMixin, self).dispatch()

    def handle_exception(self, exception, debug):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        super(CorsMixin, self).handle_exception(exception, debug)

    def options(self, *args, **kwargs):
        allowed_headers = (
            'Origin',
            'X-Requested-With',
            'Content-Type',
            'Accept',
            'X-Auth-Token',
            'X-Contentful-Content-Type',
            'Authorization',
            'X-Contentful-Version',
        )
        self.response.headers['Access-Control-Allow-Headers'] = ','.join(allowed_headers)
        self.response.headers['Access-Control-Allow-Methods'] = 'GET,PATCH,POST,PUT,DELETE'


class PublicCachingMixin(object):

    CLIENT_CACHE_TTL_SECONDS = 60  # client side cache in second
    CDN_CACHE_TTL_SECONDS = 60  # CDN / proxy cache
    CACHE_STATUS = frozenset((
        200,
        203,
        300,
        301,
        302,
        307,
        410,
    ))

    def dispatch(self):
        super(PublicCachingMixin, self).dispatch()
        if self.request.method == 'GET' and self.response.status_int in self.CACHE_STATUS:
            self.response.cache_control = 'public'
            self.response.cache_control.max_age = self.CLIENT_CACHE_TTL_SECONDS
            self.response.cache_control.s_max_age = self.CDN_CACHE_TTL_SECONDS
            self.response.md5_etag()
