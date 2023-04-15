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


def test_create_product_with_images(client: TestClient):
    login(client, username='testuser1', password='testuser1')

    # Uploading an image
    with open('./src/tests/content/image_1.png', 'rb') as f:
        response = client.post('/images', files={'image': f})
    assert response.status_code == status.HTTP_201_CREATED
    image = response.json()

    # Attaching the image to a product
    product_data = {
        'title': 'Some title',
        'stock': 10,
        'price_rub': 100,
        'images': [
            {
                'image_id': image['id'],
            },
        ],
    }
    response = client.post('/products', json=product_data)
    assert response.status_code == status.HTTP_201_CREATED

    product = response.json()
    assert len(product['images']) > 0

    response_image_id = product['images'][0]['image']['id']
    assert response_image_id == image['id']


def test_put_product_images(client: TestClient):
    login(client, username='testuser1', password='testuser1')

    # Uploading an image
    with open('./src/tests/content/image_1.png', 'rb') as f:
        response = client.post('/images', files={'image': f})
    assert response.status_code == status.HTTP_201_CREATED

    image = response.json()
    product_data = {
        'title': 'Some title',
        'stock': 10,
        'price_rub': 100,
        'images': [
            {
                'image_id': image['id'],
            },
        ],
    }
    response = client.post('/products', json=product_data)
    assert response.status_code == status.HTTP_201_CREATED

    product = response.json()
    response = client.put(f'/products/{product["id"]}', json=product_data)
    print(response.json())
    assert response.status_code == status.HTTP_200_OK

    product = response.json()
    assert len(product['images']) > 0

    response_image_id = product['images'][0]['image']['id']
    assert response_image_id == image['id']


def test_image_collision(client: TestClient):
    login(client, username='testuser1', password='testuser1')

    # Uploading an image
    with open('./src/tests/content/image_1.png', 'rb') as f:
        response = client.post('/images', files={'image': f})
    assert response.status_code == status.HTTP_201_CREATED

    # Attaching the image to a product
    image = response.json()
    product_data = {
        'title': 'Some title',
        'stock': 10,
        'price_rub': 100,
        'images': [
            {
                'image_id': image['id'],
            },
        ],
    }
    response = client.post('/products', json=product_data)
    assert response.status_code == status.HTTP_201_CREATED

    # Attaching the same image to a different product
    response = client.post('/products', json=product_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
