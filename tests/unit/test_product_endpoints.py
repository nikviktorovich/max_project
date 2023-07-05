import datetime
import uuid

import fastapi
import pytest
from fastapi import status
from fastapi import testclient

import market.modules.user.domain.models
import market.modules.product.domain.models
import market.services.auth
from market.apps.fastapi_app import deps

from .. import common


def create_test_user(username: str, repo: common.FakeUserRepository):
    auth_service = common.LightAuthService(repo) # type: ignore
    user = auth_service.register_user(uuid.uuid4(), username, 'testuser')
    token = auth_service.login(username, 'testuser')
    assert token is not None
    
    return user, common.TokenAuth(token.access_token)


def create_test_product(owner_id: uuid.UUID):
    return market.modules.product.domain.models.Product(
        id=uuid.uuid4(),
        title='Product title',
        description='Product description',
        price_rub=100.0,
        stock=10,
        owner_id=owner_id,
        added=datetime.datetime.now(),
        last_updated=datetime.datetime.now(),
    )


@pytest.mark.usefixtures('app', 'client')
def test_product_endpoint_list_products(
    lw_app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    user_repo = common.FakeUserRepository([])
    user, auth = create_test_user('owner_user', user_repo)

    product = create_test_product(user.id)
    product_repo = common.FakeProductRepository([product])
    uow = common.FakeUnitOfWork(users=user_repo, products=product_repo)
    lw_app.dependency_overrides[deps.get_uow] = lambda: uow

    response = client.get('/products')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1


@pytest.mark.usefixtures('app', 'client')
def test_product_endpoint_add_product_authorized(
    lw_app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    user_repo = common.FakeUserRepository([])
    user, auth = create_test_user('owner_user', user_repo)

    product_repo = common.FakeProductRepository([])
    uow = common.FakeUnitOfWork(users=user_repo, products=product_repo)
    lw_app.dependency_overrides[deps.get_uow] = lambda: uow

    response = client.post('/products', auth=auth, json={
        'title': 'Some title',
        'description': 'Some description',
        'stock': 10,
        'price_rub': 100.0,
    })
    assert response.status_code == status.HTTP_200_OK
    assert len(product_repo.list()) == 1


@pytest.mark.usefixtures('app', 'client')
def test_product_endpoint_add_product_unauthorized(
    lw_app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    user_repo = common.FakeUserRepository([])
    product_repo = common.FakeProductRepository([])
    uow = common.FakeUnitOfWork(users=user_repo, products=product_repo)
    lw_app.dependency_overrides[deps.get_uow] = lambda: uow

    response = client.post('/products', json={
        'title': 'Some title',
        'description': 'Some description',
        'stock': 10,
        'price_rub': 100.0,
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert len(product_repo.list()) == 0


@pytest.mark.usefixtures('app', 'client')
def test_product_endpoint_get_existing_product(
    lw_app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    user_repo = common.FakeUserRepository([])
    owner, auth = create_test_user('owner_user', user_repo)

    product = create_test_product(owner.id)
    product_repo = common.FakeProductRepository([product])
    uow = common.FakeUnitOfWork(users=user_repo, products=product_repo)
    lw_app.dependency_overrides[deps.get_uow] = lambda: uow

    response = client.get(f'/products/{product.id}')
    assert response.status_code == status.HTTP_200_OK
    assert uuid.UUID(response.json()['id']) == product.id


@pytest.mark.usefixtures('app', 'client')
def test_product_endpoint_get_nonexisting_product(
    lw_app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    user_repo = common.FakeUserRepository([])
    product_repo = common.FakeProductRepository([])
    uow = common.FakeUnitOfWork(users=user_repo, products=product_repo)
    lw_app.dependency_overrides[deps.get_uow] = lambda: uow

    response = client.get(f'/products/{uuid.uuid4()}')
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.usefixtures('app', 'client')
def test_product_endpoint_put_product_unauthorized(
    lw_app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    user_repo = common.FakeUserRepository([])
    user, auth = create_test_user('owner_user', user_repo)

    product = create_test_product(user.id)
    product_repo = common.FakeProductRepository([product])
    uow = common.FakeUnitOfWork(users=user_repo, products=product_repo)
    lw_app.dependency_overrides[deps.get_uow] = lambda: uow

    old_stock = product.stock
    response = client.put(f'/products/{product.id}', json={
        'title': 'Some title',
        'description': 'Some description',
        'stock': old_stock + 10,
        'price_rub': 100.0,
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert product_repo.get(product.id).stock == old_stock


@pytest.mark.usefixtures('app', 'client')
def test_product_endpoint_put_product_authorized_as_owner(
    lw_app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    user_repo = common.FakeUserRepository([])
    owner, owner_auth = create_test_user('owner_user', user_repo)

    product = create_test_product(owner.id)
    product_repo = common.FakeProductRepository([product])
    uow = common.FakeUnitOfWork(users=user_repo, products=product_repo)
    lw_app.dependency_overrides[deps.get_uow] = lambda: uow

    old_stock = product.stock
    response = client.put(f'/products/{product.id}', auth=owner_auth, json={
        'title': 'Some title',
        'description': 'Some description',
        'stock': old_stock + 10,
        'price_rub': 100.0,
    })
    assert response.status_code == status.HTTP_200_OK
    assert product_repo.get(product.id).stock == (old_stock + 10)


@pytest.mark.usefixtures('app', 'client')
def test_product_endpoint_put_product_authorized_as_not_owner(
    lw_app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    user_repo = common.FakeUserRepository([])
    owner, owner_auth = create_test_user('owner_user', user_repo)
    not_owner, not_owner_auth = create_test_user('not_owner_user', user_repo)

    product = create_test_product(owner.id)
    product_repo = common.FakeProductRepository([product])
    uow = common.FakeUnitOfWork(users=user_repo, products=product_repo)
    lw_app.dependency_overrides[deps.get_uow] = lambda: uow

    old_stock = product.stock
    response = client.put(f'/products/{product.id}', auth=not_owner_auth, json={
        'title': 'Some title',
        'description': 'Some description',
        'stock': old_stock + 10,
        'price_rub': 100.0,
    })
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert product_repo.get(product.id).stock == old_stock


@pytest.mark.usefixtures('app', 'client')
def test_product_endpoint_delete_product_unauthorized(
    lw_app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    user_repo = common.FakeUserRepository([])
    owner, owner_auth = create_test_user('owner_user', user_repo)

    product = create_test_product(owner.id)
    product_repo = common.FakeProductRepository([product])
    uow = common.FakeUnitOfWork(users=user_repo, products=product_repo)
    lw_app.dependency_overrides[deps.get_uow] = lambda: uow

    response = client.delete(f'/products/{product.id}')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert len(product_repo.list()) == 1


@pytest.mark.usefixtures('app', 'client')
def test_product_endpoint_delete_product_authorized_as_owner(
    lw_app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    user_repo = common.FakeUserRepository([])
    owner, owner_auth = create_test_user('owner_user', user_repo)

    product = create_test_product(owner.id)
    product_repo = common.FakeProductRepository([product])
    uow = common.FakeUnitOfWork(users=user_repo, products=product_repo)
    lw_app.dependency_overrides[deps.get_uow] = lambda: uow

    response = client.delete(f'/products/{product.id}', auth=owner_auth)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert len(product_repo.list()) == 0


@pytest.mark.usefixtures('app', 'client')
def test_product_endpoint_delete_product_authorized_as_not_owner(
    lw_app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    user_repo = common.FakeUserRepository([])
    owner, owner_auth = create_test_user('owner_user', user_repo)
    not_owner, not_owner_auth = create_test_user('not_owner_user', user_repo)

    product = create_test_product(owner.id)
    product_repo = common.FakeProductRepository([product])
    uow = common.FakeUnitOfWork(users=user_repo, products=product_repo)
    lw_app.dependency_overrides[deps.get_uow] = lambda: uow

    response = client.delete(f'/products/{product.id}', auth=not_owner_auth)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert len(product_repo.list()) == 1
