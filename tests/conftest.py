import contextlib
import uuid

import fastapi.testclient
import pytest

import market.config
import market.database.orm
import market.modules.user.repositories
import market.modules.product.domain.models
import market.modules.product.repositories
import market.services
from market.apps.fastapi_app import deps
from market.apps.fastapi_app import fastapi_main


@pytest.fixture
def client():
    return fastapi.testclient.TestClient(fastapi_main.app)


@pytest.fixture(autouse=True)
def clear_db(client):
    engine = market.config.get_database_engine()

    # In case if previous tests unexpectedly crashed and db wasn't cleared up
    market.database.orm.Base.metadata.drop_all(
        bind=engine,
    )

    with client:
        yield
    
    market.database.orm.Base.metadata.drop_all(
        bind=engine,
    )


@pytest.fixture(autouse=True)
def filled_db():
    uow_factory = contextlib.contextmanager(deps.get_uow)
    with uow_factory() as uow:
        # Adding 2 test users
        auth_service = market.services.AuthService(uow.users)

        test_user_1 = auth_service.register_user(
            user_id=uuid.uuid4(),
            username='testuser1',
            password='testuser1',
            full_name='Some Test User',
        )
        test_user_2 = auth_service.register_user(
            user_id=uuid.uuid4(),
            username='testuser2',
            password='testuser2',
            full_name='Another Test User',
        )
        
        uow.commit()
        
        
        # Adding 2 test products
        test_product_1 = market.modules.product.domain.models.Product(
            id=uuid.uuid4(),
            title='Some test product',
            stock=10,
            price_rub=1000,
            owner_id=test_user_1.id,
        )
        uow.products.add(test_product_1)

        test_product_2 = market.modules.product.domain.models.Product(
            id=uuid.uuid4(),
            title='Another test product',
            stock=0,
            price_rub=100,
            owner_id=test_user_2.id,
        )
        uow.products.add(test_product_2)

        uow.commit()
