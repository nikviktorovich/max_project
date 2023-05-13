import contextlib

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
    db_manager = contextlib.contextmanager(deps.get_db)
    with db_manager() as db:
        # Adding 2 test users
        user_repo = market.modules.user.repositories.UserRepository(db)
        auth_service = market.services.AuthService(user_repo)

        test_user_1 = auth_service.register_user(
            username='testuser1',
            password='testuser1',
            full_name='Some Test User',
        )
        test_user_2 = auth_service.register_user(
            username='testuser2',
            password='testuser2',
            full_name='Another Test User',
        )
        
        db.commit()
        
        
        # Adding 2 test products
        product_repo = market.modules.product.repositories.ProductRepository(db)

        test_product_1 = market.modules.product.domain.models.Product(
            title='Some test product',
            stock=10,
            price_rub=1000,
            owner_id=test_user_1.id,
        )
        product_repo.add(test_product_1)

        test_product_2 = market.modules.product.domain.models.Product(
            title='Another test product',
            stock=0,
            price_rub=100,
            owner_id=test_user_2.id,
        )
        product_repo.add(test_product_2)

        db.commit()
