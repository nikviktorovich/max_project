import uuid
from typing import Any
from typing import Dict
from typing import List

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from .common import login


@pytest.mark.usefixtures('client')
def upload_image(client: TestClient, path: str) -> Dict[str, Any]:
    with open(path, 'rb') as f:
        response = client.post('/images', files={'image': f})
    assert response.status_code == status.HTTP_201_CREATED

    image = response.json()
    return image


@pytest.mark.usefixtures('client')
def create_product(
    client: TestClient,
    title: str,
    stock: int,
    price_rub: float,
) -> Dict[str, Any]:
    product_data = {
        'title': title,
        'stock': stock,
        'price_rub': price_rub,
    }
    response = client.post('/products', json=product_data)
    assert response.status_code == status.HTTP_201_CREATED

    product = response.json()
    return product


@pytest.mark.usefixtures('client')
def create_product_image(
    client: TestClient,
    product_id: int,
    image_id: int,
) -> Dict[str, Any]:
    product_image_data = {
        'product_id': product_id,
        'image_id': image_id,
    }
    response = client.post('/productimages', json=product_image_data)
    assert response.status_code == status.HTTP_201_CREATED

    product_image = response.json()
    return product_image


@pytest.mark.usefixtures('client')
def list_product_images(
    client: TestClient,
    product_id: uuid.UUID,
) -> List[Dict[str, Any]]:
    response = client.get(f'/productimages?product_id={product_id}')
    assert response.status_code == status.HTTP_200_OK

    product_image_list = response.json()
    return product_image_list


@pytest.mark.usefixtures('clear_db', 'client')
def test_create_product_with_images(client: TestClient):
    login(client, username='testuser1', password='testuser1')

    image = upload_image(client, './tests/content/image_1.png')
    product = create_product(
        client,
        title='Test product',
        stock=10,
        price_rub=100.0,
    )
    product_image = create_product_image(client, product['id'], image['id'])
    product_image_list = list_product_images(client, product['id'])
    
    assert len(product_image_list) > 0
    assert product_image_list[0] == product_image