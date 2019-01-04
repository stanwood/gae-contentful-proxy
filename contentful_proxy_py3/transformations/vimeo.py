import datetime
import json
import logging

import dateutil.parser
import requests

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class VimeoTransformation:
    """
    Replace all Vimeo IDs with Vimeo API response.
    """

    VIMEO_URL = 'https://api.vimeo.com/videos/{video_id}?fields=download'

    def __init__(self, vimeo_token, cache_get, cache_set):
        self.vimeo_token = vimeo_token
        self.cache_get = cache_get
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

    def _get_vimeo_content(self, video_id, token):
        cache_key = 'VIMEO_{}'.format(video_id)

        cached_response = self.cache_get(cache_key)

        if cached_response:
            return json.loads(cached_response)

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
        for index, item in enumerate(content['items']):
            if item['fields'].get('video'):
                content['items'][index]['fields']['video'] = self._get_vimeo_content(
                    item['fields'].get('video'),
                    self.vimeo_token,
                )
