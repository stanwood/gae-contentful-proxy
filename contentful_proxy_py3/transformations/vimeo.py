import datetime
import json

import dateutil.parser
import requests

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class VimeoTransformation:
    """
    Replace all Vimeo IDs with Vimeo API response.
    """

    CACHE_PREFIX = 'VIMEO_CACHE'
    VIMEO_URL = 'https://api.vimeo.com/videos/{video_id}?fields=download'

    def __init__(self, vimeo_token, cache_get, cache_mget, cache_set):
        self.vimeo_token = vimeo_token
        self.cache_get = cache_get
        self.cache_mget = cache_mget
        self.cache_set = cache_set

    @staticmethod
    def _request_session():
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=1)
        session.mount('https://', HTTPAdapter(max_retries=retries))
        return session

    @classmethod
    def _calculate_expiration_time(cls, expiration_datetime):
        now = datetime.datetime.utcnow()
        expiration = dateutil.parser.parse(
            expiration_datetime
        ).replace(tzinfo=None)
        return int((expiration - now).total_seconds()) - 120

    def _get_vimeo_cache(self, vimeo_ids):
        return self.cache_mget(vimeo_ids)

    def _get_vimeo_content(self, video_id, token):
        cache_key = f'{self.CACHE_PREFIX}:{video_id}'

        session = self._request_session()
        response = session.get(
            self.VIMEO_URL.format(video_id=video_id),
            headers={'Authorization': 'Bearer {}'.format(token)}
        ).json()

        self.cache_set(
            cache_key,
            json.dumps(response['download']),
            self._calculate_expiration_time(
                response['download'][0]['expires']
            )
        )

        return response['download']

    def __call__(self, content):
        vimeo_ids = set([
            f"{self.CACHE_PREFIX}:{item['fields'].get('video')}"
            for item in content['items']
            if item['fields'].get('video')
        ])

        vimeo_cache = {}

        if vimeo_ids:
            vimeo_cache = dict(
                zip(
                    vimeo_ids,
                    self.cache_mget(vimeo_ids)
                )
            )

        for index, item in enumerate(content['items']):
            vimeo_id = item['fields'].get('video')  # temporary

            if item['fields'].get('video'):
                vimeo_data = vimeo_cache.get(
                    f"{self.CACHE_PREFIX}:{item['fields'].get('video')}"
                )

                if not vimeo_data:
                    vimeo_data = self._get_vimeo_content(
                        item['fields'].get('video'),
                        self.vimeo_token
                    )
                else:
                    vimeo_data = json.loads(vimeo_data)

                content['items'][index]['fields']['video'] = vimeo_data
                content['items'][index]['fields']['vimeo'] = vimeo_id
