import collections


class ResolveIncludes:
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
                    obj_id = obj['sys']['id']
                    try:
                        obj = includes[obj['sys']['linkType']][obj_id]
                    except KeyError:
                        pass
                    else:
                        obj['id'] = obj_id

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
