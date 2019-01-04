from urllib.parse import urlparse


class ReplaceAssetLinks:

    def __init__(self, proxy_hostname):
        self.proxy_hostname = proxy_hostname

    def transform_url(self, url):
        original_url = urlparse(url)
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
