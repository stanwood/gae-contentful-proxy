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
import urllib

from contentful.errors import EntryNotFoundError
from google.appengine.api import urlfetch

from stanwood.handlers.exceptions import RequestError


class ContentfulManagementClient(object):

    CONTENTFUL_CM_URL = 'https://api.contentful.com'

    def __init__(self, contentful_management_token):
        """
        Init.

        Args:
            contentful_management_token (str): Contentful management token.
        """

        self.CONTENTFUL_MANAGEMENT_TOKEN = contentful_management_token

    @staticmethod
    def get_entry_version(created_entry_response):
        """
        Return entry version.

        Args:
            created_entry_response (json): Response from self.create_entry().

        Returns:
            Entry version as a string.
        """
        entry_version = created_entry_response['sys']['version']

        return entry_version

    @staticmethod
    def get_entry_id(created_entry_response):
        """
        Return entry id
        Args:
            created_entry_response: json as string

        Returns:
            Entry id as string.

        """

        return json.loads(created_entry_response)['sys']['id']

    def make_request(self, url, headers=None, method=urlfetch.GET, **kwargs):

        request_headers = {
            'Authorization': 'Bearer {}'.format(self.CONTENTFUL_MANAGEMENT_TOKEN),
        }
        if headers:
            request_headers.update(headers)

        return urlfetch.fetch(
            method=method,
            url=url,
            headers=request_headers,
            **kwargs
        )

    def get_entry_by_id(self, space_id, content_type_id, entry_id):

        request_url = '{}/spaces/{}/environments/master/entries/{}'.format(
            self.CONTENTFUL_CM_URL, space_id, entry_id
        )
        headers = {
            'Content-Type': 'application/vnd.contentful.management.v1+json',
            'X-Contentful-Content-Type': content_type_id
        }
        response = self.make_request(request_url, headers=headers)

        if response.status_code == 404:
            raise EntryNotFoundError(
                "Entry not found for ID: '{}'".format(entry_id)
            )

        if response.status_code / 400:
            raise RequestError(
                '{} {}'.format(response.status_code, response.content)
            )

        return response

    def search_entry_by_field(self, space_id, content_type_id, field_name, field_value):

        request_url = '{}/spaces/{}/environments/master/entries?&content_type={}&{}[match]={}'.format(
            self.CONTENTFUL_CM_URL,
            space_id,
            content_type_id,
            field_name,
            urllib.quote_plus(field_value.encode('utf-8'))
        )
        headers = {
            'Content-Type': 'application/vnd.contentful.management.v1+json',
            'X-Contentful-Content-Type': content_type_id
        }
        response = self.make_request(request_url, headers=headers)

        if response.status_code == 404:
            raise EntryNotFoundError(
                "Entry not found for query: '{0}={1}'".format(field_name, field_value)
            )

        if response.status_code / 400:
            raise RequestError(
                '{} {}'.format(response.status_code, response.content)
            )

        return json.loads(response.content)

    def create_or_update_entry(self, space_id, content_type_id, entry_id, version, data):
        """
        Create or update an entry. If entry does not exist, it will create it
        with given entry_id.

        Args:
            space_id (str): Contentful Space ID.
            content_type_id (str): Contentful Content type ID.
            entry_id (str): Contentful Entry ID.
            data (dict): Data which should be stored in Contentful.

        Returns:
            Contentful API response.

        Exceptions:
            RequestError - Contentful API request error.
        """

        if not entry_id:
            request_url = '{}/spaces/{}/environments/master/entries'.format(
                self.CONTENTFUL_CM_URL, space_id
            )
        else:
            request_url = '{}/spaces/{}/environments/master/entries/{}'.format(
                self.CONTENTFUL_CM_URL, space_id, entry_id
            )

        headers = {
            'Content-Type': 'application/vnd.contentful.management.v1+json',
            'X-Contentful-Content-Type': content_type_id
        }
        if version:
            headers['X-Contentful-Version'] = version

        response = self.make_request(
            request_url,
            method=urlfetch.PUT if entry_id else urlfetch.POST,
            headers=headers,
            payload=json.dumps(data),
        )

        if response.status_code / 400:
            raise RequestError(
                '{} {}'.format(response.status_code, response.content)
            )

        return json.loads(response.content)

    def publish_entry(self, space_id, entry_id, version):
        """
        Publish an entry.

        Args:
            space_id (str): Contentful Space ID.
            entry_id (str): Contentful Entry ID.
            version (str): Contentful Entry version. It is returned in
                response from self.create_entry().

        Returns:
            Contentful API response.

        Exceptions:
            RequestError - Contentful API request error.
        """

        request_url = '{}/spaces/{}/environments/master/entries/{}/published'.format(
            self.CONTENTFUL_CM_URL, space_id, entry_id
        )
        headers = {'X-Contentful-Version': version}

        response = self.make_request(
            method=urlfetch.PUT,
            url=request_url,
            headers=headers
        )

        if response.status_code / 400:
            raise RequestError(
                '{} {}'.format(response.status_code, response.content)
            )

        return json.loads(response.content)

    def unpublish_entry(self, space_id, entry_id, version):
        """
        Unpublish an entry.

        Args:
            space_id (str): Contentful Space ID.
            entry_id (str): Contentful Entry ID.
            version (str): Contentful Entry version. It is returned in
                response from self.create_entry().

        Returns:
            Contentful API response.

        Exceptions:
            RequestError - Contentful API request error.
        """

        request_url = '{}/spaces/{}/environments/master/entries/{}/published'.format(
            self.CONTENTFUL_CM_URL, space_id, entry_id
        )
        headers = {'X-Contentful-Version': version}
        response = self.make_request(
            method=urlfetch.DELETE,
            url=request_url,
            headers=headers,
        )

        if response.status_code / 400:
            raise RequestError(
                '{} {}'.format(response.status_code, response.content)
            )

        return json.loads(response.content)
