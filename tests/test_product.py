from fastapi import status
from fastapi.testclient import TestClient

from .fixtures import clear_db
from .fixtures import client
from .fixtures import filled_db
from .fixtures import overriden_app
from .common import login


def test_product_create(client: TestClient):
    login(client, username='testuser1', password='testuser1')

    # Adding a product
    product_data = {
        'title': 'Some title',
        'stock': 10,
        'price_rub': 100,
    }
    response = client.post('/products', json=product_data)
    assert response.status_code == status.HTTP_201_CREATED
