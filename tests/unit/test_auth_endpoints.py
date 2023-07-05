import uuid

import fastapi
import pytest
from fastapi import status
from fastapi import testclient

import market.services.auth
from market.apps.fastapi_app import deps

from .. import common


@pytest.mark.usefixtures('app', 'client')
def test_auth_endpoint_signup(app: fastapi.FastAPI, client: testclient.TestClient):
    user_repo = common.FakeUserRepository([])
    uow = common.FakeUnitOfWork(users=user_repo)
    app.dependency_overrides[deps.get_uow] = lambda: uow

    response = client.post('/signup', data={
        'username': 'username',
        'password': 'password',
    })
    assert response.status_code == status.HTTP_200_OK
    assert 'access_token' in response.json()


@pytest.mark.usefixtures('app', 'client')
def test_auth_endpoint_login(app: fastapi.FastAPI, client: testclient.TestClient):
    user_repo = common.FakeUserRepository([])
    uow = common.FakeUnitOfWork(users=user_repo)
    app.dependency_overrides[deps.get_uow] = lambda: uow

    response = client.post('/token', data={
        'username': 'username',
        'password': 'password',
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    auth_service = market.services.auth.AuthServiceImpl(uow.users)
    auth_service.register_user(uuid.uuid4(), 'username', 'password')

    response = client.post('/token', data={
        'username': 'username',
        'password': 'password',
    })
    assert response.status_code == status.HTTP_200_OK
