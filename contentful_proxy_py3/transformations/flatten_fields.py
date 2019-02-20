import logging

import rich_text_renderer
from rich_text_renderer.base_node_renderer import BaseNodeRenderer


class ImageRenderer(BaseNodeRenderer):
    IMAGE_HTML = '<img src="{0}" alt="{1}" />'

    def render(self, node):
        entry = node['data']['target']

        return self.IMAGE_HTML.format(
            entry['file']['url'], entry['title']
        )


class FlattenFields(object):
    renderer = rich_text_renderer.RichTextRenderer(
        {
            'embedded-asset-block': ImageRenderer
        }
    )

    @classmethod
    def _flatten_image_field(cls, field_value):
        value = {
            'url': field_value['file']['url'],
            'width': field_value['file']['details']['image']['width'],
            'height': field_value['file']['details']['image']['height'],
        }

        try:
            value['title'] = field_value['title']
        except KeyError:
            pass

        return value

    @staticmethod
    def _get_value_id(value):
        try:
            return value['sys']['id']
        except (TypeError, KeyError):
            return None

    @classmethod
    def flatten_field(cls, field_value):
        # Flatten richText fields
        try:
            return cls.renderer.render(field_value)
        except Exception:  # It is really raised
            pass

        if isinstance(field_value, (str, bool, int, float)):
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
                for key, value in fields.items()
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
