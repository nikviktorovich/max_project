import pytest
from fastapi import status
from fastapi.testclient import TestClient

from .common import login


@pytest.mark.usefixtures('client')
def test_upload(client: TestClient):
    login(client, username='testuser1', password='testuser1')

    with open('./tests/content/image_1.png', 'rb') as f:
        response = client.post('/images', files={'image': f})
    assert response.status_code == status.HTTP_200_OK
