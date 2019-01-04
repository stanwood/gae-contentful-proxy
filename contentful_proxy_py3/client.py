import hashlib
import json

from urllib.parse import urlencode

from abc import (
    ABC,
    abstractmethod,
    abstractproperty
)

import contentful
import requests

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from . import transformations


class ContentfulClient(ABC):
    CACHE_TTL = 60*60
    CACHE_PREFIX = 'contentful'
    CONTENTFUL_CDN_URL = 'http://cdn.contentful.com'

    @abstractproperty
    def _contentful_space(self):
        pass

    @abstractproperty
    def _contentful_token(self):
        pass

    @property
    def _contentful(self):
        return contentful.Client(
            self._contentful_space,
            self._contentful_token,
            content_type_cache=False,
        )

    @abstractproperty
    def _vimeo_token(self):
        pass

    @abstractproperty
    def _cache_client(self):
        pass

    @abstractmethod
    def _cache_get(self, cache_key: str) -> object:
        pass

    @abstractmethod
    def _cache_set(self, cache_key: str, content: str, expiration_time: int):
        pass

    @abstractproperty
    def _proxy_hostname(self):
        pass

    def _contentful_cache_key(
        self,
        item_type: str = None,
        item_id: int = None,
        query: dict = None
    ):
        return f'{self.CACHE_PREFIX}:{item_type}:{item_id}?{json.dumps(query)}'

    @property
    def _contentful_transformations(self):
        return [
            transformations.ReplaceAssetLinks(
                proxy_hostname=self._proxy_hostname
            ),
            transformations.ResolveIncludes(),
            transformations.VimeoTransformation(
                self._vimeo_token,
                self._cache_get,
                self._cache_set,
            ),
            transformations.FlattenFields(),
            transformations.RemoveIncludes(),
            transformations.RemoveRootSys(),
        ]

    def _calculate_md5(self, json_data: str):
        return hashlib.md5(json_data).hexdigest()

    @staticmethod
    def _request_session():
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=1)
        session.mount('https://', HTTPAdapter(max_retries=retries))
        return session

    def _generate_request_url(
        self,
        item_type: str = None,
        item_id: int = None,
        query: dict = None
    ):
        request_url = f'{self.CONTENTFUL_CDN_URL}/spaces/{self._contentful_space}/{item_type}'
        query_string = {}

        if item_id:
            query_string = {'sys.id': item_id}

        if query:
            query_string = {**query_string, **query}

        if query_string:
            return f'{request_url}?{urlencode(query_string)}'

        return request_url

    def contentful_get(
        self,
        item_type: str = None,
        item_id: int = None,
        query: dict = None
    ):
        cache_key = self._contentful_cache_key(
            item_type, item_id, query
        )

        response = self._cache_get(cache_key)
        if response:
            return json.loads(response), self._calculate_md5(response)

        session = self._request_session()
        response = session.get(
            self._generate_request_url(
                item_type, item_id, query
            ),
            headers={
                'Authorization': f'Bearer {self._contentful_token}'
            }
        ).json()

        for transformation in self._contentful_transformations:
            transformation(response)

        json_response = json.dumps(response)

        self._cache_set(cache_key, json_response, self.CACHE_TTL)

        return response, self._calculate_md5(json_response.encode('utf-8'))
