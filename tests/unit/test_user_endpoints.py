import uuid

import fastapi
import pytest
from fastapi import status
from fastapi import testclient

import market.modules.user.domain.models
import market.services.auth
from market.apps.fastapi_app import deps

from .. import common


def create_test_user(username: str, repo: common.FakeUserRepository):
    auth_service = common.LightAuthService(repo) # type: ignore
    user = auth_service.register_user(uuid.uuid4(), username, 'testuser')
    token = auth_service.login(username, 'testuser')
    assert token is not None
    
    return user, common.TokenAuth(token.access_token)


@pytest.mark.usefixtures('app', 'client')
def test_user_endpoint_get_user_unauthorized(
    lw_app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    user_repo = common.FakeUserRepository([])
    uow = common.FakeUnitOfWork(users=user_repo)
    lw_app.dependency_overrides[deps.get_uow] = lambda: uow

    response = client.get('/user')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.usefixtures('app', 'client')
def test_user_endpoint_get_user_authorized(
    lw_app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    user_repo = common.FakeUserRepository([])
    user, auth = create_test_user('testuser', user_repo)

    uow = common.FakeUnitOfWork(users=user_repo)
    lw_app.dependency_overrides[deps.get_uow] = lambda: uow

    response = client.get('/user', auth=auth)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == 'testuser'


@pytest.mark.usefixtures('app', 'client')
def test_user_endpoint_put_user_unauthorized(
    lw_app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    user_repo = common.FakeUserRepository([])
    uow = common.FakeUnitOfWork(users=user_repo)
    lw_app.dependency_overrides[deps.get_uow] = lambda: uow

    response = client.put('/user', json={
        'full_name': 'Some Full Name',
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.usefixtures('app', 'client')
def test_user_endpoint_put_user_authorized(
    lw_app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    user_repo = common.FakeUserRepository([])
    user, auth = create_test_user('testuser', user_repo)

    uow = common.FakeUnitOfWork(users=user_repo)
    lw_app.dependency_overrides[deps.get_uow] = lambda: uow

    new_name = user.full_name + ' New'
    response = client.put('/user', auth=auth, json={
        'full_name': new_name,
    })
    assert response.status_code == status.HTTP_200_OK
    assert user_repo.get(user.id).full_name == new_name
