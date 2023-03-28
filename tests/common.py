from fastapi import status
from fastapi.testclient import TestClient


def login(client: TestClient, username: str, password: str) -> None:
    response = client.post('/token', data={
        'username': username,
        'password': password,
    })
    assert response.status_code == status.HTTP_200_OK

    token = response.json()
    client.headers['Authorization'] = f'Bearer {token["access_token"]}'
