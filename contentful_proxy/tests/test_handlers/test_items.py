import mock
import pytest


@pytest.fixture
def contentful():
    with mock.patch(
            'contentful_proxy.handlers.items.DetailProxyHandler.contentful',
            new_callable=mock.PropertyMock
    ) as mock_types:
        yield mock_types


def test_get_item_by_id(app, contentful):
    contentful.return_value.content_type.return_value = mock.MagicMock(content='{}')
    item_type, item_id = 'content_types', '124'
    response = app.get('/contentful/{}/{}'.format(item_type, item_id))

    assert response.status_code == 200

    contentful.return_value.content_type.assert_called_once_with(item_id)


def test_get_item(app, contentful):
    contentful.return_value.content_types.return_value = mock.MagicMock(content='{}')
    item_type = 'content_types'
    response = app.get('/contentful/{}'.format(item_type))

    assert response.status_code == 200

    contentful.return_value.content_types.assert_called_once_with({})


def test_get_item_root_path(app, contentful):
    contentful.return_value.root_endpoint.return_value = mock.MagicMock(content='{}')
    response = app.get('/contentful/')

    assert response.status_code == 200

    contentful.return_value.root_endpoint.assert_called_once_with({})


def test_get_item_unexpected_type(app, contentful):
    app.get('/contentful/unexpected-type', status=404)
