import pytest
from fastapi import status
from fastapi.testclient import TestClient

from .common import login


@pytest.mark.usefixtures('clear_db', 'client')
def test_cart_create(client: TestClient):
    # Checking for restriction of unauthorized access
    response = client.get('/cart')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    login(client, username='testuser1', password='testuser1')

    # Checking if the empty cart works as expected
    response = client.get('/cart')
    assert response.status_code == status.HTTP_200_OK

    # Adding a test product
    response = client.post('/products', json={
        'title': 'Some title',
        'stock': 10,
        'price_rub': 100.0,
    })
    assert response.status_code == status.HTTP_201_CREATED
    product = response.json()
    product_id = product['id']

    # Adding a product to cart
    response = client.post('/cart', json={
        'product_id': product_id,
        'amount': 2,
    })
    assert response.status_code == status.HTTP_201_CREATED

    # Getting the created cart item
    response = client.get(f'/products/{product_id}')
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.usefixtures('clear_db', 'client')
def test_cart_collision(client: TestClient):
    login(client, username='testuser1', password='testuser1')

    # Adding a test product
    response = client.post('/products', json={
        'title': 'Some title',
        'stock': 10,
        'price_rub': 100.0,
    })
    assert response.status_code == status.HTTP_201_CREATED
    product = response.json()
    product_id = product['id']

    # Adding the same product to cart twice
    response = client.post('/cart', json={
        'product_id': product_id,
        'amount': 10,
    })
    assert response.status_code == status.HTTP_201_CREATED

    response = client.post('/cart', json={
        'product_id': product_id,
        'amount': 10,
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.usefixtures('clear_db', 'client')
def test_cart_update(client: TestClient):
    login(client, username='testuser1', password='testuser1')

    response = client.get('/cart')
    assert response.status_code == status.HTTP_200_OK

    # Adding a test product
    response = client.post('/products', json={
        'title': 'Some title',
        'stock': 10,
        'price_rub': 100.0,
    })
    assert response.status_code == status.HTTP_201_CREATED
    product = response.json()

    # Adding a test product in cart
    cart_item_data = {
        'amount': 1,
        'product_id': product['id'],
    }

    response = client.post('/cart', json=cart_item_data)
    assert response.status_code == status.HTTP_201_CREATED
    created_cart_item = response.json()
    created_cart_item_id = created_cart_item['id']

    # Updating cart item data
    cart_item_data['amount'] = 10
    response = client.put(f'/cart/{created_cart_item_id}', json=cart_item_data)
    assert response.status_code == status.HTTP_200_OK

    updated_cart_item = response.json()
    assert updated_cart_item['amount'] == 10
