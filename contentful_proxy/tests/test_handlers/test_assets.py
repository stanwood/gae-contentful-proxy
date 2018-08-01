import json

import mock


def test_download_file(app, google_cloud_storage, contentful_client):
    from contentful_proxy.handlers import assets
    asset_id = '1234'
    contentful_content = {
        'fields': {
            'file': {
                'contentType': 'application/json',
                'url': 'path/to/file.json',
            },
        },
    }

    contentful_client.asset.return_value = mock.MagicMock(
        content=json.dumps(contentful_content),
        status_code=200,
    )

    response = app.get('/contentful/download/{}'.format(asset_id))

    assert response.status_code == 302
    assert response.location.endswith(contentful_content['fields']['file']['url'])
    assert response.content_type == contentful_content['fields']['file']['contentType']
    assert response.cache_control.header_value == (
        'max-age={}, public, s-maxage={}'
    ).format(
        assets.DownloadHandler.CDN_CACHE_TTL_SECONDS,
        assets.DownloadHandler.CLIENT_CACHE_TTL_SECONDS
    )

    contentful_client.asset.assert_called_with(asset_id)


def test_download_file_not_found(app, google_cloud_storage, contentful_client):
    contentful_client.asset.return_value = mock.MagicMock(
        content=json.dumps({}),
        status_code=404,
    )

    app.get('/contentful/download/{}'.format('123'), status=404)


def test_download_file_json_parsing_error(app, google_cloud_storage, contentful_client):
    contentful_client.asset.return_value = mock.MagicMock(
        status_code=200,
    )

    app.get('/contentful/download/{}'.format('123'), status=404)


