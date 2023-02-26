import unittest
import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm
import database
import main
from fastapi import status
from fastapi.testclient import TestClient


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


main.app.dependency_overrides[main.get_db] = get_test_db

client = TestClient(main.app)


class TestAPI(unittest.TestCase):
    def setUp(self) -> None:
        database.Base.metadata.create_all(bind=engine)
    
    def tearDown(self) -> None:
        database.Base.metadata.drop_all(bind=engine)
    
    def test_permissions(self):
        response = client.get('/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse('token' in response.json())
        
        response = client.get('/products')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_registering(self):
        # Needs to be authorized
        response = client.get('/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # No data specified
        response = client.post('/signup')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        # Username and password are too short
        data = {
            'username': 'short',
            'password': 'short'
        }
        response = client.post('/signup', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Successful registering
        data = {
            'username': 'username',
            'password': 'password'
        }
        response = client.post('/signup', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.json()
        
        # Successful calling index while being authorized
        headers = {'Authorization': f'Bearer {token["access_token"]}'}
        response = client.get('/', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
