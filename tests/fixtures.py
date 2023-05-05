import fastapi.testclient
import pytest
import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm

from market import database
from market import deps
from market import domain
from market import main
from market import repositories
from market import services


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
    database.orm.Base.metadata.drop_all(bind=engine)
    database.orm.Base.metadata.create_all(bind=engine)
    yield
    database.orm.Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True, scope="module")
def filled_db():
    with TestingSessionLocal() as db:
        # Adding 2 test users
        user_repo = repositories.UserRepository(db)
        auth_service = services.AuthService(user_repo)

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
        product_repo = repositories.ProductRepository(db)

        test_product_1 = domain.models.Product(
            title='Some test product',
            stock=10,
            price_rub=1000,
            owner_id=test_user_1.id,
        )
        product_repo.add(test_product_1)

        test_product_2 = domain.models.Product(
            title='Another test product',
            stock=0,
            price_rub=100,
            owner_id=test_user_2.id,
        )
        product_repo.add(test_product_2)

        db.commit()


@pytest.fixture(autouse=True)
def overriden_app():
    main.app.dependency_overrides[deps.get_db] = get_test_db
    yield main.app
    del main.app.dependency_overrides[deps.get_db]


@pytest.fixture
def client():
    return fastapi.testclient.TestClient(main.app)
