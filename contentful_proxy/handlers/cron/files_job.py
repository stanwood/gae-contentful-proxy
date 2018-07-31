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
import datetime
import logging

import webapp2
from google.appengine.api import memcache

from contentful_proxy.utils.handlers import storage
from contentful_proxy.utils.handlers import webapp2_base
from contentful_proxy.models import files


class CleanupCachedFilesHandler(webapp2_base.CustomBaseHandler, storage.CloudClient):
    TTL_DAYS = 30

    @webapp2.cached_property
    def model(self):
        return files.ContentfulFile

    def get(self):
        """
        Clears old files from Google Cloud Storage and Google Datastore.

        Usage:
            curl -X GET "https://{domain}.appspot.com/_ah/cron/clean-up-files" (logged in as google admin)
        """

        logging.info("Removing files older than {} days".format(self.TTL_DAYS))

        old_files = self.model.query(
            self.model.created <= datetime.datetime.utcnow() - datetime.timedelta(days=self.TTL_DAYS)
        )

        for contentful_file in old_files:
            logging.debug(u"Deleting {}".format(contentful_file.name))

            contentful_file.key.delete()
            blob = self.bucket.blob(contentful_file.name)
            blob.delete()

            try:
                memcache.delete(contentful_file.memcache_key)
            except AttributeError:
                logging.warning("Could not remove url from memcache.")
