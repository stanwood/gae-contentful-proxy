import mock
import pytest


@pytest.fixture
def urlfetch():
    with mock.patch('contentful_proxy.handlers.files.urlfetch') as mock_urlfetch:
        mock_urlfetch.fetch.return_value = mock.MagicMock(
            content='file_data',
            headers={},
        )
        yield mock_urlfetch


@pytest.fixture
def gcs_blob():
    blob = mock.MagicMock(
        public_url='test_public_url',
    )
    blob.name = 'test_blob_name'

    yield blob


def test_get_file_not_cached(app, google_cloud_storage, urlfetch, gcs_blob):
    from contentful_proxy.models import files
    google_cloud_storage.return_value.bucket.return_value.blob.return_value = gcs_blob

    assert files.ContentfulFile.query().count() == 0

    response = app.get('/contentful/file_cache/source/test_file')

    assert response.status_code == 303

    contentful_files = files.ContentfulFile.query().fetch()

    assert len(contentful_files) == 1
    assert contentful_files[0].name == gcs_blob.name
    assert contentful_files[0].public_url == gcs_blob.public_url


def test_get_cached_file(app, google_cloud_storage, urlfetch, gcs_blob):
    from contentful_proxy.models import files
    google_cloud_storage.return_value.bucket.return_value.blob.return_value = gcs_blob

    assert files.ContentfulFile.query().count() == 0

    response = app.get('/contentful/file_cache/source/test_file')

    assert response.status_code == 303

    contentful_files = files.ContentfulFile.query().fetch()

    assert len(contentful_files) == 1
    assert contentful_files[0].name == gcs_blob.name
    assert contentful_files[0].public_url == gcs_blob.public_url

    urlfetch_call_count = urlfetch.fetch.call_count
    google_cloud_storage_call_count = google_cloud_storage.return_value.bucket.return_value.blob.call_count

    cached_response = app.get('/contentful/file_cache/source/test_file')

    assert cached_response.status_code == 303
    assert urlfetch_call_count == urlfetch.fetch.call_count
    assert google_cloud_storage.return_value.bucket.return_value.blob.call_count == google_cloud_storage_call_count


