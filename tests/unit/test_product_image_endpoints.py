import datetime
import uuid

import fastapi
import pytest
from fastapi import status
from fastapi import testclient

import market.modules.image.domain.models
import market.modules.product.domain.models
import market.modules.product_image.domain.models
import market.modules.user.domain.models
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
def test_product_image_endpoint_list_product_images(
    app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    user_repo = common.FakeUserRepository([])
    owner, owner_auth = create_test_user('owner_user', user_repo)

    product_with_images = create_test_product(owner.id)
    product_with_no_images = create_test_product(owner.id)
    products_repo = common.FakeProductRepository([
        product_with_images,
        product_with_no_images,
    ])

    image = market.modules.image.domain.models.Image(
        id=uuid.uuid4(),
        image='filename.png',
    )
    images_repo = common.FakeImageRepository([image])

    product_images_repo = common.FakeProductImageRepository([
        market.modules.product_image.domain.models.ProductImage(
            id=uuid.uuid4(),
            product_id=product_with_images.id,
            image_id=image.id,
        ),
    ])
    uow = common.FakeUnitOfWork(
        users=user_repo,
        products=products_repo,
        images=images_repo,
        product_images=product_images_repo,
    )
    app.dependency_overrides[deps.get_uow] = lambda: uow

    response = client.get(f'/productimages?product_id={product_with_images.id}')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1

    response = client.get(f'/productimages?product_id={product_with_no_images.id}')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 0

    response = client.get(f'/productimages?product_id={uuid.uuid4()}')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 0


@pytest.mark.usefixtures('app', 'client')
def test_product_image_endpoint_add_product_image_unauthorized(
    app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    user_repo = common.FakeUserRepository([])
    owner, owner_auth = create_test_user('owner_user', user_repo)

    product = create_test_product(owner.id)
    products_repo = common.FakeProductRepository([product])

    image = market.modules.image.domain.models.Image(
        id=uuid.uuid4(),
        image='filename.png',
    )
    images_repo = common.FakeImageRepository([image])

    product_images_repo = common.FakeProductImageRepository([])
    uow = common.FakeUnitOfWork(
        users=user_repo,
        products=products_repo,
        images=images_repo,
        product_images=product_images_repo,
    )
    app.dependency_overrides[deps.get_uow] = lambda: uow

    response = client.post('/productimages', json={
        'product_id': str(product.id),
        'image_id': str(image.id),
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert len(product_images_repo.list()) == 0


@pytest.mark.usefixtures('app', 'client')
def test_product_image_endpoint_add_product_image_as_owner(
    app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    user_repo = common.FakeUserRepository([])
    owner, owner_auth = create_test_user('owner_user', user_repo)

    product = create_test_product(owner.id)
    products_repo = common.FakeProductRepository([product])

    image = market.modules.image.domain.models.Image(
        id=uuid.uuid4(),
        image='filename.png',
    )
    images_repo = common.FakeImageRepository([image])

    product_images_repo = common.FakeProductImageRepository([])
    uow = common.FakeUnitOfWork(
        users=user_repo,
        products=products_repo,
        images=images_repo,
        product_images=product_images_repo,
    )
    app.dependency_overrides[deps.get_uow] = lambda: uow

    response = client.post('/productimages', auth=owner_auth, json={
        'product_id': str(product.id),
        'image_id': str(image.id),
    })
    assert response.status_code == status.HTTP_200_OK
    assert len(product_images_repo.list()) == 1


@pytest.mark.usefixtures('app', 'client')
def test_product_image_endpoint_add_product_image_as_not_owner(
    app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    user_repo = common.FakeUserRepository([])
    owner, owner_auth = create_test_user('owner_user', user_repo)
    not_owner, not_owner_auth = create_test_user('not_owner_user', user_repo)

    product = create_test_product(owner.id)
    products_repo = common.FakeProductRepository([product])

    image = market.modules.image.domain.models.Image(
        id=uuid.uuid4(),
        image='filename.png',
    )
    images_repo = common.FakeImageRepository([image])

    product_images_repo = common.FakeProductImageRepository([])
    uow = common.FakeUnitOfWork(
        users=user_repo,
        products=products_repo,
        images=images_repo,
        product_images=product_images_repo,
    )
    app.dependency_overrides[deps.get_uow] = lambda: uow

    response = client.post('/productimages', auth=not_owner_auth, json={
        'product_id': str(product.id),
        'image_id': str(image.id),
    })
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert len(product_images_repo.list()) == 0


@pytest.mark.usefixtures('app', 'client')
def test_product_image_endpoint_add_product_image_nonexisting_image(
    app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    user_repo = common.FakeUserRepository([])
    owner, owner_auth = create_test_user('owner_user', user_repo)

    product = create_test_product(owner.id)
    products_repo = common.FakeProductRepository([product])
    images_repo = common.FakeImageRepository([])

    product_images_repo = common.FakeProductImageRepository([])
    uow = common.FakeUnitOfWork(
        users=user_repo,
        products=products_repo,
        images=images_repo,
        product_images=product_images_repo,
    )
    app.dependency_overrides[deps.get_uow] = lambda: uow

    response = client.post('/productimages', auth=owner_auth, json={
        'product_id': str(product.id),
        'image_id': str(uuid.uuid4()),
    })
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.usefixtures('app', 'client')
def test_product_image_endpoint_add_product_image_nonexisting_product(
    app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    user_repo = common.FakeUserRepository([])
    owner, owner_auth = create_test_user('owner_user', user_repo)

    products_repo = common.FakeProductRepository([])

    image = market.modules.image.domain.models.Image(
        id=uuid.uuid4(),
        image='filename.png',
    )
    images_repo = common.FakeImageRepository([image])

    product_images_repo = common.FakeProductImageRepository([])
    uow = common.FakeUnitOfWork(
        users=user_repo,
        products=products_repo,
        images=images_repo,
        product_images=product_images_repo,
    )
    app.dependency_overrides[deps.get_uow] = lambda: uow

    response = client.post('/productimages', auth=owner_auth, json={
        'product_id': str(uuid.uuid4()),
        'image_id': str(image.id),
    })
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.usefixtures('app', 'client')
def test_product_image_endpoint_get_existing_product_image(
    app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    user_repo = common.FakeUserRepository([])
    owner, owner_auth = create_test_user('owner_user', user_repo)

    product = create_test_product(owner.id)
    products_repo = common.FakeProductRepository([product])

    image = market.modules.image.domain.models.Image(
        id=uuid.uuid4(),
        image='filename.png',
    )
    images_repo = common.FakeImageRepository([image])

    product_image = market.modules.product_image.domain.models.ProductImage(
        id=uuid.uuid4(),
        product_id=product.id,
        image_id=image.id,
    )
    product_images_repo = common.FakeProductImageRepository([product_image])
    uow = common.FakeUnitOfWork(
        users=user_repo,
        products=products_repo,
        images=images_repo,
        product_images=product_images_repo,
    )
    app.dependency_overrides[deps.get_uow] = lambda: uow

    response = client.get(f'/productimages/{product_image.id}')
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.usefixtures('app', 'client')
def test_product_image_endpoint_get_nonexisting_product_image(
    app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    user_repo = common.FakeUserRepository([])
    owner, owner_auth = create_test_user('owner_user', user_repo)

    product = create_test_product(owner.id)
    products_repo = common.FakeProductRepository([product])

    image = market.modules.image.domain.models.Image(
        id=uuid.uuid4(),
        image='filename.png',
    )
    images_repo = common.FakeImageRepository([image])
    product_images_repo = common.FakeProductImageRepository([])
    uow = common.FakeUnitOfWork(
        users=user_repo,
        products=products_repo,
        images=images_repo,
        product_images=product_images_repo,
    )
    app.dependency_overrides[deps.get_uow] = lambda: uow

    response = client.get(f'/productimages/{uuid.uuid4()}')
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.usefixtures('app', 'client')
def test_product_image_endpoint_delete_product_image_unauthorized(
    app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    user_repo = common.FakeUserRepository([])
    owner, owner_auth = create_test_user('owner_user', user_repo)

    product = create_test_product(owner.id)
    products_repo = common.FakeProductRepository([product])

    image = market.modules.image.domain.models.Image(
        id=uuid.uuid4(),
        image='filename.png',
    )
    images_repo = common.FakeImageRepository([image])

    product_image = market.modules.product_image.domain.models.ProductImage(
        id=uuid.uuid4(),
        product_id=product.id,
        image_id=image.id,
    )
    product_images_repo = common.FakeProductImageRepository([product_image])
    uow = common.FakeUnitOfWork(
        users=user_repo,
        products=products_repo,
        images=images_repo,
        product_images=product_images_repo,
    )
    app.dependency_overrides[deps.get_uow] = lambda: uow

    response = client.delete(f'/productimages/{product_image.id}')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert len(product_images_repo.list()) == 1


@pytest.mark.usefixtures('app', 'client')
def test_product_image_endpoint_delete_product_image_as_owner(
    app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    user_repo = common.FakeUserRepository([])
    owner, owner_auth = create_test_user('owner_user', user_repo)

    product = create_test_product(owner.id)
    products_repo = common.FakeProductRepository([product])

    image = market.modules.image.domain.models.Image(
        id=uuid.uuid4(),
        image='filename.png',
    )
    images_repo = common.FakeImageRepository([image])

    product_image = market.modules.product_image.domain.models.ProductImage(
        id=uuid.uuid4(),
        product_id=product.id,
        image_id=image.id,
    )
    product_images_repo = common.FakeProductImageRepository([product_image])
    uow = common.FakeUnitOfWork(
        users=user_repo,
        products=products_repo,
        images=images_repo,
        product_images=product_images_repo,
    )
    app.dependency_overrides[deps.get_uow] = lambda: uow

    response = client.delete(f'/productimages/{product_image.id}', auth=owner_auth)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert len(product_images_repo.list()) == 0


@pytest.mark.usefixtures('app', 'client')
def test_product_image_endpoint_delete_product_image_as_not_owner(
    app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    user_repo = common.FakeUserRepository([])
    owner, owner_auth = create_test_user('owner_user', user_repo)
    not_owner, not_owner_auth = create_test_user('not_owner_user', user_repo)

    product = create_test_product(owner.id)
    products_repo = common.FakeProductRepository([product])

    image = market.modules.image.domain.models.Image(
        id=uuid.uuid4(),
        image='filename.png',
    )
    images_repo = common.FakeImageRepository([image])

    product_image = market.modules.product_image.domain.models.ProductImage(
        id=uuid.uuid4(),
        product_id=product.id,
        image_id=image.id,
    )
    product_images_repo = common.FakeProductImageRepository([product_image])
    uow = common.FakeUnitOfWork(
        users=user_repo,
        products=products_repo,
        images=images_repo,
        product_images=product_images_repo,
    )
    app.dependency_overrides[deps.get_uow] = lambda: uow

    response = client.delete(
        f'/productimages/{product_image.id}',
        auth=not_owner_auth,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert len(product_images_repo.list()) == 1
