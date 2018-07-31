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
import abc
import logging

from contentful_proxy.handlers.mixins import base as base_mixin
from contentful_proxy.utils.handlers import webapp2_base


class DetailProxyHandler(base_mixin.ClientMixin, webapp2_base.PublicCachingMixin, webapp2_base.CustomBaseHandler):
    __metaclass__ = abc.ABCMeta

    @property
    def types(self):
        """
        Mapping for item name and get item method.

        :return: Dict for each item with key as a name of item and value as
                 a list of singular and plural get methods for items.
        :rtype: dict
        """
        return {
            'content_types': [self.contentful.content_type, self.contentful.content_types],
            'entries': [self.contentful.entry, self.contentful.entries],
            'assets': [self.contentful.asset, self.contentful.assets],
            None: [self.contentful.root_endpoint, self.contentful.root_endpoint]
        }

    def get(self, item_type=None, item_id=None):
        """
        Get the content model of a space or get a single content type.
        Supports multiple routing paths.

        :param item_type: Type of item (can be empty)
        :param item_id: Item ID (can be empty)

        API Reference: https://www.contentful.com/developers/docs/references/content-delivery-api

        Usage:
            curl -X GET "https://{domain}.appspot.com/contentful/"
            curl -X GET "https://{domain}.appspot.com/contentful/{item_type}"
            curl -X GET "https://{domain}.appspot.com/contentful/{item_type}/{item_id}"
        """
        try:
            if item_id:
                response = self.types[item_type][0](item_id)
            else:
                query = dict(self.request.params.items())
                logging.debug(query)
                response = self.types[item_type][1](query)

        except KeyError as key_error:
            logging.error("Unexpected item type `{}`".format(key_error))
            return self.abort(code=404)

        self.response.write(response.content)
        self.response.content_type = 'application/json'
