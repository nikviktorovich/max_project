import unittest
import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm
import auth
import database
import main
from fastapi import status
from fastapi.testclient import TestClient
from database import crud
from database import models
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
            test_product_1 = models.Product(
                title='Some test product',
                description='',
                stock=10,
                price_rub=1000,
                owner=crud.get_user_by_username(db, 'testuser1'),
            )
            test_product_2 = models.Product(
                title='Another test product',
                description='',
                stock=0,
                price_rub=100,
                owner=crud.get_user_by_username(db, 'testuser2'),
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
    
    def test_product_detail(self):
        # Getting product with id 1, added during setup stage
        response = client.get('/products/1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_product(self):
        product_payload = {
            'title': 'Some title',
            'stock': 10,
            'price_rub': 100,
        }

        # Testing adding a product being unauthorized
        response = client.post('products', json=product_payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Logging in
        login_data = {
            'username': 'testuser1',
            'password': 'testuser1'
        }
        response = client.post('/token', data=login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.json()
        
        # Successful calling index while being authorized
        headers = {'Authorization': f'Bearer {token["access_token"]}'}
        response = client.post('/products', headers=headers, json=product_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        added_product = response.json()

        # Testing adding a product
        response = client.get(f'/products')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(added_product, response.json())
    
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
    
    def test_add_product_image(self):
        response = client.get('/products')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        products = response.json()
        product_id = products[0]['id']

        with open('./test_content/test_image_1.png', 'rb') as f:
            response = client.post('/images', files={'image_file': f})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        image_id = response.json()['id']

        payload = {'image_id': image_id}
        response = client.post(f'/products/{product_id}/addImage', json=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_patch_product(self):
        # Getting any random first test product
        response = client.get('/products')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        products = response.json()
        test_product = products[0]

        # Adding stock count
        product_stock = test_product['stock']
        patch_data = {
            'stock': product_stock + 1,
        }

        # Patching product record
        product_id = test_product['id']
        response = client.patch(f'/products/{product_id}', json=patch_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Checking if patch is applied
        patched_product = response.json()
        self.assertEqual(patched_product['stock'], product_stock + 1)

        response = client.get(f'/products/{product_id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), patched_product)
    
    def test_patch_user_fullname(self):
        # Trying to patch while not authorized
        response = client.patch('/user', json={
            'full_name': 'New Full Name',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Logging in
        response = client.post('/token', data={
            'username': 'testuser1',
            'password': 'testuser1',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.json()
        headers = {'Authorization': f'Bearer {token["access_token"]}'}

        # Patching users full name
        response = client.patch('/user', headers=headers, json={
            'full_name': 'New Full Name',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['full_name'], 'New Full Name')
