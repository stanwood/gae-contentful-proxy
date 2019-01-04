class RemoveIncludes:
    """
    Remove includes array from response.
    """

    def __call__(self, content):
        try:
            del content['includes']
        except KeyError:
            return content
