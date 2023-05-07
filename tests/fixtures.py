import fastapi.testclient
import pytest
import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm

import market.database.orm
import market.modules.user.repositories
import market.modules.product.domain.models
import market.modules.product.repositories
import market.services
from market.apps.fastapi_app import deps
from market.apps.fastapi_app import fastapi_main


SQLALCHEMY_DATABASE_URL = 'sqlite:///./test_market_app.db'

engine = sqlalchemy.create_engine(
    url=SQLALCHEMY_DATABASE_URL,
    connect_args={'check_same_thread': False}
)

TestingSessionLocal = sqlalchemy.orm.sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


def get_test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True, scope="module")
def clear_db():
    market.database.orm.Base.metadata.drop_all(bind=engine)
    market.database.orm.Base.metadata.create_all(bind=engine)
    yield
    market.database.orm.Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True, scope="module")
def filled_db():
    with TestingSessionLocal() as db:
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


@pytest.fixture(autouse=True)
def overriden_app():
    fastapi_main.app.dependency_overrides[deps.get_db] = get_test_db
    yield fastapi_main.app
    del fastapi_main.app.dependency_overrides[deps.get_db]


@pytest.fixture
def client():
    return fastapi.testclient.TestClient(fastapi_main.app)
