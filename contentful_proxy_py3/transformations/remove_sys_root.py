class RemoveRootSys:
    def __call__(self, content):
        try:
            del content['sys']
        except KeyError:
            return content
