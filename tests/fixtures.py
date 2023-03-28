import fastapi.testclient
import pytest
import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm
import auth
import database
import deps
import main
from database import crud
from database import schemas


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
    database.Base.metadata.drop_all(bind=engine)
    database.Base.metadata.create_all(bind=engine)
    yield
    database.Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True, scope="module")
def filled_db():
    with TestingSessionLocal() as db:
        # Adding 2 test users
        users = [
            schemas.UserCreate(
                username='testuser1',
                password='testuser1',
                full_name='Some Test User',
            ),
            schemas.UserCreate(
                username='testuser2',
                password='testuser2',
                full_name='Another Test User'
            )
        ]

        for user in users:
            auth.register_user(db, user)
        
        
        # Adding 2 test products
        test_product_1 = schemas.ProductCreate(
            title='Some test product',
            description='',
            stock=10,
            price_rub=1000,
        )
        test_user_1 = crud.get_user_by_username(db, 'testuser1')
        crud.add_product(db, test_product_1, test_user_1)

        test_product_2 = schemas.ProductCreate(
            title='Another test product',
            description='',
            stock=0,
            price_rub=100,
        )
        test_user_2 = crud.get_user_by_username(db, 'testuser2')
        crud.add_product(db, test_product_2, test_user_2)
        
        db.commit()


@pytest.fixture(autouse=True)
def overriden_app():
    main.app.dependency_overrides[deps.get_db] = get_test_db
    yield main.app
    del main.app.dependency_overrides[deps.get_db]


@pytest.fixture
def client():
    return fastapi.testclient.TestClient(main.app)
