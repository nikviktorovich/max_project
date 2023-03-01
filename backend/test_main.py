import unittest
import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm
import database
import main
from fastapi import status
from fastapi.testclient import TestClient
from database import models


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
    @classmethod
    def setUpClass(cls) -> None:
        database.Base.metadata.create_all(bind=engine)
        cls.fill_db(cls)
    
    def fill_db(self) -> None:
        with TestingSessionLocal() as db:
            # Adding 2 test users
            test_user_1 = models.User(
                username='testuser1',
                password='testuser1',
                full_name='Some Test User',
            )
            test_user_2 = models.User(
                username='testuser2',
                password='testuser2',
                full_name='Another Test User'
            )
            users = [test_user_1, test_user_2]
            db.add_all(users)
            
            # Adding 2 test products
            test_product_1 = models.Product(
                title='Some test product',
                description='',
                stock=10,
                price_rub=1000,
                owner=test_user_1,
            )
            test_product_2 = models.Product(
                title='Another test product',
                description='',
                stock=0,
                price_rub=100,
                owner=test_user_2,
            )
            products = [test_product_1, test_product_2]
            db.add_all(products)
            
            db.commit()
    
    @classmethod
    def tearDownClass(cls) -> None:
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
    
    def test_products_list(self):
        # Testing getting products list
        response = client.get('/products')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json())
    
    def test_image_upload(self):
        # No upload file presented
        response = client.post('/image')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Uploading a valid file
        with open('./test_content/test_image_1.png', 'rb') as f:
            response = client.post('/images', files={'image_file': f})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        image_id = response.json()['id']

        # Checking for the image presence
        response = client.get(f'/images/{image_id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
