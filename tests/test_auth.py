import pytest
from fastapi import status
from fastapi.testclient import TestClient


@pytest.mark.usefixtures('clear_db', 'client')
def test_registering(client: TestClient):
    # No data specified
    response = client.post('/signup')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Username and password are too short
    data = {
        'username': 'short',
        'password': 'short'
    }
    response = client.post('/signup', data=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    # Successful registering
    data = {
        'username': 'username',
        'password': 'password'
    }
    response = client.post('/signup', data=data)
    assert response.status_code == status.HTTP_200_OK
    token = response.json()
    
    # Successful calling index while being authorized
    headers = {'Authorization': f'Bearer {token["access_token"]}'}
    response = client.get('/cart', headers=headers)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.usefixtures('clear_db', 'client')
def test_login(client: TestClient):
    data = {
        'username': 'testuser1',
        'password': 'testuser1',
    }
    response = client.post('/token', data=data)
    assert response.status_code == status.HTTP_200_OK
