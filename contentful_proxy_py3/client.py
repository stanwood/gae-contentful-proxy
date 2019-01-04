import hashlib
import json

from abc import (
    ABC,
    abstractmethod,
    abstractproperty
)

import contentful

from . import transformations


class ContentfulClient(ABC):
    CACHE_TTL = 60*60
    CACHE_PREFIX = 'contentful'

    @abstractproperty
    def _contentful_space(self):
        pass

    @abstractproperty
    def _contentful_token(self):
        pass

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
    def _contentful(self):
        return contentful.Client(
            self._contentful_space,
            self._contentful_token,
            raw_mode=True,
            content_type_cache=False,
        )

    @property
    def _types(self):

        return {
            'content_types': [
                self._contentful.content_type,
                self._contentful.content_types
            ],
            'entries': [
                self._contentful.entry,
                self._contentful.entries
            ],
            'assets': [
                self._contentful.asset,
                self._contentful.assets
            ],
            None: [
                self._contentful.space,
                self._contentful.space
            ]
        }

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

        if item_id:
            response = self._types[item_type][0](item_id, query=query).json()
        else:
            response = self._types[item_type][1](query).json()

        for transformation in self._contentful_transformations:
            transformation(response)

        json_response = json.dumps(response)

        self._cache_set(cache_key, json_response, self.CACHE_TTL)

        return response, self._calculate_md5(json_response.encode('utf-8'))
