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
import logging

from contentful_proxy.handlers.mixins import base as mixin_base
from contentful_proxy.utils.handlers import webapp2_base


class DownloadHandler(mixin_base.ClientMixin, webapp2_base.PublicCachingMixin, webapp2_base.CustomBaseHandler):

    def get(self, asset_id):
        """
        Fetches and downloads asset from Contentful.
        API Reference: https://www.contentful.com/developers/docs/references/content-delivery-api/#/reference/assets/asset/get-a-single-asset

        :param asset_id: The ID of the target Asset.

        Usage:
            curl -X GET "https://{domain}.appspot.com/contentful/download/{asset_id}"
        """

        response = self.contentful.asset(asset_id)
        if response.status_code / 400:
            logging.debug(response.content)
            return self.abort(404, "Asset not found")

        try:
            asset = json.loads(response.content)
        except (KeyError, TypeError) as ex:
            logging.exception(ex)
            logging.error("Key {} not found.".format(ex))

            self.abort(404, "Asset not found")
        else:
            self.response.content_type = asset['fields']['file'].get(
                'contentType',
                u'application/octet-stream'
            ).encode('utf-8')

            self.redirect(
                asset['fields']['file']['url'].encode('utf-8')
            )
