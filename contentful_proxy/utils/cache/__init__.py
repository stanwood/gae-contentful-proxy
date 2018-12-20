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
import hashlib
import json
import logging

import contentful
from contentful.errors import EntryNotFoundError
from google.appengine.api import memcache

from . import transformations


class CachedResponse(object):

    def __init__(self, content, status_code):
        self.content = content
        self.status_code = status_code

    def json(self):
        return json.loads(self.content)


class Client(contentful.Client):
    CACHE_TTL = 10

    def __init__(self, *args, **kwargs):
        self.CONTENT_TRANSFORMATIONS = kwargs.pop('transformations')
        kwargs['raw_mode'] = True   # do not want any transformation of responses
        super(Client, self).__init__(*args, **kwargs)

    def memcache_key(self, url, query):
        return u'contentful:{}:{}:{}?{}'.format(
            self.space_id,
            url,
            hashlib.md5(str(self.CONTENT_TRANSFORMATIONS)).hexdigest(),
            json.dumps(query)
        )

    def entry(self, entry_id, query=None):

        if query is None:
            query = {}
        self._normalize_select(query)

        query.update({'sys.id': entry_id})
        response = self._get(
            '/entries',
            query
        )

        if self.raw_mode:
            return response

        try:
            response[0]
        except IndexError:
            raise EntryNotFoundError(
                "Entry not found for ID: '{0}'".format(entry_id)
            )

    def _http_get(self, url, query):
        memcache_key = self.memcache_key(url, query)

        content = memcache.get(memcache_key)
        if content is not None:
            logging.debug("Cached contentful response {}".format(memcache_key))

            return CachedResponse(
                content=content,
                status_code=204,
            )

        response = super(Client, self)._http_get(url, query)
        if response.status_code != 200:
            raise contentful.errors.get_error(response)

        content = response.content

        try:
            content = json.loads(content)
        except ValueError:
            pass
        else:
            for transformation in self.CONTENT_TRANSFORMATIONS:
                transformation(content)

            content = json.dumps(content)

        response = CachedResponse(
            content=content,
            status_code=response.status_code
        )

        try:
            memcache.set(
                memcache_key,
                content,
                time=self.CACHE_TTL
            )
        except ValueError as ex:
            logging.exception(ex)
            logging.error("Failed to cache contentful response")

        return response

    def root_endpoint(self, query):
        return super(Client, self)._get('/', query)
