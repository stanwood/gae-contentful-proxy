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
import collections
import logging
import urlparse


class ReplaceAssetLinks(object):

    def __init__(self, proxy_hostname):
        self.proxy_hostname = proxy_hostname

    def transform_url(self, url):
        original_url = urlparse.urlparse(url)
        path = '/'.join(original_url.path.split('/')[1:])
        proxy_url = '{}/contentful/file_cache/{}/{}'.format(
            self.proxy_hostname,
            original_url.hostname,
            path
        )
        return proxy_url

    def __call__(self, content):
        try:
            for asset in content['includes']['Asset']:
                asset['fields']['file']['url'] = self.transform_url(asset['fields']['file']['url'])
        except (TypeError, KeyError):
            pass

        try:
            for asset in content['items']:
                if asset['sys']['type'] == 'Asset':
                    asset['fields']['file']['url'] = self.transform_url(asset['fields']['file']['url'])
        except (TypeError, KeyError):
            pass


class ResolveIncludes(object):
    """
    Replace all Contentful link types with data from includes.
    """

    def __call__(self, content):
        try:
            # Do not modify content if it does not contain includes and items
            unmodified_includes = content['includes']
            unmodified_items = content['items']
        except KeyError:
            return content

        includes = collections.defaultdict(dict)

        for key, values in unmodified_includes.items():
            for value in values:
                includes[key][value['sys']['id']] = value['fields']

        def transform_content(obj):
            if isinstance(obj, dict):
                try:
                    if not obj['sys']['type'] == 'Link' or not obj['sys']['linkType'] in ['Asset', 'Entry']:
                        raise TypeError
                except (TypeError, KeyError):
                    pass
                else:
                    obj = includes[obj['sys']['linkType']][obj['sys']['id']]

                return {
                    key: transform_content(value)
                    for key, value in obj.items()
                }
            elif isinstance(obj, list):
                return [transform_content(element) for element in obj]
            else:
                return obj

        content['items'] = transform_content(unmodified_items)

        return content


class RemoveIncludes(object):
    """
    Remove includes array from response.
    """

    def __call__(self, content):
        try:
            del content['includes']
        except KeyError:
            return content


class RemoveRootSys(object):
    def __call__(self, content):
        try:
            del content['sys']
        except KeyError:
            return content


class FlattenFields(object):

    @classmethod
    def _flatten_image_field(cls, field_value):
        return {
            'url': field_value['file']['url'],
            'width': field_value['file']['details']['image']['width'],
            'height': field_value['file']['details']['image']['height'],
        }

    @staticmethod
    def _get_value_id(value):
        try:
            return value['sys']['id']
        except (TypeError, KeyError):
            return None

    @classmethod
    def flatten_field(cls, field_value):
        if isinstance(field_value, (basestring, bool, int, float)):
            # No flattening
            return field_value
        elif isinstance(field_value, list):
            # Detect fields type (Asset or Entry).
            try:
                field_value[0]['file']['contentType']  # Asset
            except (TypeError, KeyError):
                # Entry type, it can be a list of items from another content type (relationship).
                return [cls.flatten_fields(v) for v in field_value]
            else:
                # Asset type, it can be a list of images.
                return [cls.flatten_field(v) for v in field_value]

        # Flatten image
        try:
            return cls._flatten_image_field(field_value)
        except (TypeError, KeyError):
            pass

        # link to movie
        try:
            return field_value['file']['url']
        except (TypeError, KeyError):
            pass

        # link to pdf file
        try:
            return field_value['pdf']['fields']['file']['url']
        except (TypeError, KeyError):
            pass

        # empty link to pdf file if asset is missing
        try:
            if field_value['pdf'] is None:
                return ''
        except (TypeError, KeyError):
            pass

        # flatten embedded entry
        try:
            return cls.flatten_fields(
                field_value['fields'],
                cls._get_value_id(field_value)
            )
        except (TypeError, KeyError):
            pass

        # return id of linked entry which was not resolved
        try:
            return {
                'id': field_value['sys']['id']
            }
        except (TypeError, KeyError):
            pass

        logging.warning(
            u'Failed to flatten field value: {}'.format(field_value)
        )

        return field_value

    @classmethod
    def flatten_fields(cls, fields, item_id=None):
        if isinstance(fields, dict):
            fields = {
                key: cls.flatten_field(value)
                for key, value in fields.iteritems()
                if value is not None
            }

            if item_id is not None:
                fields['id'] = item_id

            return fields

        return fields

    def __call__(self, content):
        content['items'] = [
            self.flatten_fields(entry['fields'], entry['sys']['id'])
            for entry in content.get('items', [])
        ]

        return content
