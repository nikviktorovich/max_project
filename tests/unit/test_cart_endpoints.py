import datetime
import uuid

import fastapi
import pytest
from fastapi import status
from fastapi import testclient

import market.modules.product.domain.models
import market.modules.cart.domain.models
import market.services.auth
from market.apps.fastapi_app import deps

from .. import common


def create_test_user(username: str, repo: common.FakeUserRepository):
    auth_service = market.services.auth.AuthServiceImpl(repo) # type: ignore
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
def test_cart_endpoint_get_cart_items_authorized(
    app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    user_repo = common.FakeUserRepository([])
    user, auth = create_test_user('testuser', user_repo)

    product = create_test_product(user.id)
    product_repo = common.FakeProductRepository([product])
    cart_repo = common.FakeCartRepository([
        market.modules.cart.domain.models.CartItem(
            id=uuid.uuid4(),
            product_id=product.id,
            user_id=user.id,
            amount=1,
        ),
    ])
    uow = common.FakeUnitOfWork(
        users=user_repo,
        products=product_repo,
        cart=cart_repo,
    )
    app.dependency_overrides[deps.get_uow] = lambda: uow

    response = client.get('/cart', auth=auth)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1


@pytest.mark.usefixtures('app', 'client')
def test_cart_endpoint_get_cart_items_unauthorized(
    app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    user_repo = common.FakeUserRepository([])
    user, _ = create_test_user('testuser', user_repo)

    product = create_test_product(user.id)
    product_repo = common.FakeProductRepository([product])
    cart_repo = common.FakeCartRepository([])
    uow = common.FakeUnitOfWork(
        users=user_repo,
        products=product_repo,
        cart=cart_repo,
    )
    app.dependency_overrides[deps.get_uow] = lambda: uow

    response = client.get('/cart')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.usefixtures('app', 'client')
def test_cart_endpoint_add_cart_item_success(
    app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    user_repo = common.FakeUserRepository([])
    user, auth = create_test_user('testuser', user_repo)

    product = create_test_product(user.id)
    product_repo = common.FakeProductRepository([product])
    cart_repo = common.FakeCartRepository([])
    uow = common.FakeUnitOfWork(
        users=user_repo,
        products=product_repo,
        cart=cart_repo,
    )
    app.dependency_overrides[deps.get_uow] = lambda: uow

    response = client.post('/cart', auth=auth, json={
        'product_id': str(product.id),
        'amount': 1,
    })
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.usefixtures('app', 'client')
def test_cart_endpoint_add_cart_item_failure(
    app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    user_repo = common.FakeUserRepository([])
    user, auth = create_test_user('testuser', user_repo)

    product = create_test_product(user.id)
    product_repo = common.FakeProductRepository([product])
    cart_repo = common.FakeCartRepository([])
    uow = common.FakeUnitOfWork(
        users=user_repo,
        products=product_repo,
        cart=cart_repo,
    )
    app.dependency_overrides[deps.get_uow] = lambda: uow

    # Adding a product to the cart
    response = client.post('/cart', auth=auth, json={
        'product_id': str(product.id),
        'amount': 1,
    })
    assert response.status_code == status.HTTP_200_OK

    # Adding the same product second time
    response = client.post('/cart', auth=auth, json={
        'product_id': str(product.id),
        'amount': 1,
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_cart_endpoint_get_cart_item_by_owner(
    app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    user_repo = common.FakeUserRepository([])
    user, auth = create_test_user('testuser', user_repo)

    product = create_test_product(user.id)
    product_repo = common.FakeProductRepository([product])

    cart_item = market.modules.cart.domain.models.CartItem(
        id=uuid.uuid4(),
        product_id=product.id,
        user_id=user.id,
        amount=3,
    )
    cart_repo = common.FakeCartRepository([cart_item])
    uow = common.FakeUnitOfWork(
        users=user_repo,
        products=product_repo,
        cart=cart_repo,
    )
    app.dependency_overrides[deps.get_uow] = lambda: uow

    response = client.get(f'/cart/{cart_item.id}', auth=auth)
    assert response.status_code == status.HTTP_200_OK
    assert uuid.UUID(response.json()['id']) == cart_item.id


def test_cart_endpoint_get_cart_item_not_by_owner(
    app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    user_repo = common.FakeUserRepository([])
    owner, owner_auth = create_test_user('owner_user', user_repo)
    not_owner, not_owner_auth = create_test_user('not_owner_user', user_repo)

    product = create_test_product(owner.id)
    product_repo = common.FakeProductRepository([product])

    cart_item = market.modules.cart.domain.models.CartItem(
        id=uuid.uuid4(),
        product_id=product.id,
        user_id=owner.id,
        amount=3,
    )
    cart_repo = common.FakeCartRepository([cart_item])
    uow = common.FakeUnitOfWork(
        users=user_repo,
        products=product_repo,
        cart=cart_repo,
    )
    app.dependency_overrides[deps.get_uow] = lambda: uow

    response = client.get(f'/cart/{cart_item.id}', auth=not_owner_auth)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_cart_endpoint_put_cart_item_by_owner(
    app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    user_repo = common.FakeUserRepository([])
    owner, owner_auth = create_test_user('owner_user', user_repo)

    product = create_test_product(owner.id)
    product_repo = common.FakeProductRepository([product])

    cart_item = market.modules.cart.domain.models.CartItem(
        id=uuid.uuid4(),
        product_id=product.id,
        user_id=owner.id,
        amount=3,
    )
    cart_repo = common.FakeCartRepository([cart_item])
    uow = common.FakeUnitOfWork(
        users=user_repo,
        products=product_repo,
        cart=cart_repo,
    )
    app.dependency_overrides[deps.get_uow] = lambda: uow

    response = client.put(f'/cart/{cart_item.id}', auth=owner_auth, json={
        'product_id': str(product.id),
        'amount': 1,
    })
    assert response.status_code == status.HTTP_200_OK
    assert cart_repo.get(cart_item.id).amount == 1
