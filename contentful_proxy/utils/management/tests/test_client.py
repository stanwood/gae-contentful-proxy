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
import mock
import pytest

from stanwood.external_services.contentful.utils.management.client import ContentfulManagementClient
from stanwood.handlers.exceptions import RequestError


CONTENTFUL_MANAGEMENT_TOKEN = 'token'

client = ContentfulManagementClient(CONTENTFUL_MANAGEMENT_TOKEN)


@pytest.fixture
def http_request(testbed):
    with mock.patch('stanwood.external_services.contentful.utils.management.client.urlfetch.fetch') as urlfetch_mock:
        yield urlfetch_mock


def test_create_entry(http_request):
    http_request.return_value = mock.Mock(status_code=200, content='{}')

    client.create_or_update_entry('space_id', 'content_type_id', 'entry_id', 1, {'data': 1})

    assert http_request.called_with(
        headers={
            'Content-Type': 'application/vnd.contentful.management.v1+json',
            'Authorization': 'Bearer {}'.format(CONTENTFUL_MANAGEMENT_TOKEN),
            'X-Contentful-Content-Type': 'content_type_id',
            'X-Contentful-Version': 1,
        },
        method=4,
        payload='{"data": 1}',
        url='https://api.contentful.com/spaces/space_id/entries/entry_id'
    )


def test_create_entry_request_error(http_request):
    http_request.return_value = mock.Mock(status_code=400, content='Error')

    with pytest.raises(RequestError):
        client.create_or_update_entry('space_id', 'content_type_id', 'entry_id', 1, {'data': 1})


def test_publish_entry(http_request):
    http_request.return_value = mock.Mock(status_code=200, content='{}')

    client.publish_entry('space_id', 'entry_id', 'version')

    assert http_request.called_with(
        headers={
            'X-Contentful-Version': 'version',
            'Authorization': 'Bearer {}'.format(CONTENTFUL_MANAGEMENT_TOKEN)
        },
        method=4,
        url='https://api.contentful.com/spaces/space_id/entries/entry_id/published'
    )


def test_publish_entry_request_error(http_request):
    http_request.return_value = mock.Mock(status_code=400, content='Error')

    with pytest.raises(RequestError):
        client.publish_entry('space_id', 'entry_id', 'version')


def test_get_entry_by_id(http_request):
    http_request.return_value = mock.Mock(status_code=200)

    client.get_entry_by_id('space_id', 'content_type_id', 'entry_id')

    assert http_request.called_with(
        headers={
            'X-Contentful-Content-Type': 'content_type_id',
            'Authorization': 'Bearer {}'.format(CONTENTFUL_MANAGEMENT_TOKEN),
            'Content-Type': 'application/vnd.contentful.management.v1+json',
        },
        method=4,
        url='https://api.contentful.com/spaces/space_id/environments/master/entries/entry_id'
    )
