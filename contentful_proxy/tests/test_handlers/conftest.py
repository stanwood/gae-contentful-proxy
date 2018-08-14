import mock
import pytest


@pytest.fixture
def google_cloud_storage():
    with mock.patch(
        'contentful_proxy.utils.handlers.storage.CloudClient.storage',
        new_callable=mock.PropertyMock
    ) as mock_storage:
        yield mock_storage


@pytest.fixture
def contentful_client():
    with mock.patch('contentful_proxy.utils.cache.Client') as mock_contentful_client:
        yield mock_contentful_client.return_value
