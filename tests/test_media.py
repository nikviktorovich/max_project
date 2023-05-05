from fastapi import status
from fastapi.testclient import TestClient

from .fixtures import clear_db
from .fixtures import client
from .fixtures import filled_db
from .fixtures import overriden_app
from .common import login


def test_upload(client: TestClient):
    login(client, username='testuser1', password='testuser1')

    with open('./tests/content/image_1.png', 'rb') as f:
        response = client.post('/images', files={'image': f})
    assert response.status_code == status.HTTP_201_CREATED
