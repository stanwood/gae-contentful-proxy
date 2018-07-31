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
import os

import webapp2
from google.appengine.api import urlfetch

from contentful_proxy.utils.handlers import webapp2_base


class ProxyHandler(webapp2_base.CorsMixin, webapp2.RequestHandler):
    CONTENTFUL_URL = 'https://api.contentful.com/'

    @property
    def contentful_management_token(self):
        return os.environ['CONTENTFUL_MANAGEMENT_TOKEN']

    @property
    def contentful_space(self):
        return os.environ['CONTENTFUL_SPACE']

    @webapp2.cached_property
    def endpoint(self):
        return self.request.route_kwargs.pop('endpoint')

    @property
    def contentful_request(self):
        if not self.endpoint.startswith('spaces'):
            return u'spaces/{}/{}?{}'.format(
                self.contentful_space,
                self.endpoint,
                self.request.query_string
            )
        else:
            return u'{}?{}'.format(self.endpoint, self.request.query_string)

    def dispatch(self):
        if self.request.method != 'OPTIONS':

            headers = dict(self.request.headers.items())
            headers.update(
                {
                    'Authorization': 'Bearer {}'.format(self.contentful_management_token)
                }
            )

            response = urlfetch.fetch(
                self.CONTENTFUL_URL + self.contentful_request,
                payload=self.request.body,
                method=self.request.method,
                headers=headers,
                deadline=60
            )

            response.headers.pop('content-length', None)
            self.response.headers = response.headers
            self.response.write(response.content)
            self.response.status_int = response.status_code
        else:
            super(ProxyHandler, self).dispatch()
