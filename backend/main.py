import logging
import os.path
import sqlalchemy.exc
import auth
import database
import deps
from typing import List
from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import security
from fastapi import status
from fastapi.middleware import cors
from sqlalchemy.orm import Session
from database import crud
from database import models
from database import schemas

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

database.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# CORS configuration
origins = [
    'http://localhost:*',
]

app.add_middleware(
    middleware_class=cors.CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


# Routes

# Auth

@app.get('/')
async def get_index(token: str = Depends(auth.oauth2_scheme)):
    return {'token': token}


@app.post('/token')
async def login(
    form_data: security.OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(deps.get_db)
):
    """
    Returns:
        access_token
        token_type
    """
    login_result = auth.login(db, form_data.username, form_data.password)
    if login_result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    return login_result


@app.post('/signup')
async def signup(token: schemas.Token = Depends(deps.register_user)):
    """
    """
    
    return token


# User

@app.patch('/user', response_model=schemas.UserRead)
def patch_username(
    user_patch: schemas.UserFullnameUpdate,
    user: models.User = Depends(deps.get_user),
    db: Session = Depends(deps.get_db)
):
    patched_user = crud.patch_user_fullname(db, user.id, user_patch)

    if patched_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You need to authorize first',
        )
    
    return patched_user


@app.put('/user', response_model=schemas.UserRead)
def put_username(
    user_put: schemas.UserFullnamePut,
    user: models.User = Depends(deps.get_user),
    db: Session = Depends(deps.get_db)
):
    updated_user = crud.put_user_fullname(db, user.id, user_put)

    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You need to authorize first',
        )
    
    return updated_user


# Products

@app.get('/products', response_model=List[schemas.ProductRead])
def get_products(
    offset: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db)
):
    return crud.get_products(db, offset, limit)


@app.post(
    '/products',
    response_model=schemas.ProductRead,
    status_code=status.HTTP_201_CREATED,
)
def add_product(
    product: schemas.ProductCreate,
    owner: models.User = Depends(deps.get_user),
    db: Session = Depends(deps.get_db),
):
    product_model = crud.add_product(db, product, owner)
    if product_model is None:
        logger.error(
            f'Failed adding product. User: {owner.username}, Product: {product}'
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Unable to add product',
        )
    return product_model


@app.get('/products/{product_id}', response_model=schemas.ProductRead)
def get_product(product_id: int, db: Session = Depends(deps.get_db)):
    product_model = crud.get_product_by_id(db, product_id)
    if product_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Unable to find a product with the specified id',
        )
    return product_model


@app.patch('/products/{product_id}', response_model=schemas.ProductRead)
def patch_product(
    product_id: int,
    product_patch: schemas.ProductUpdate,
    user: models.User = Depends(deps.get_user),
    db: Session = Depends(deps.get_db)
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not authorized',
        )
    
    product = crud.get_product_by_id(db, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Unable to find a product with the specified id',
        )
    
    # Check if user is an owner of this product
    if user.id != product.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Insufficient permissions',
        )

    patched_product = crud.patch_product(db, product_id, product_patch)

    if patched_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Unable to find a product with the specified id',
        )
    
    return patched_product


@app.put('/products/{product_id}', response_model=schemas.ProductRead)
def put_product(
    product_id: int,
    product_put: schemas.ProductPut,
    user: models.User = Depends(deps.get_user),
    db: Session = Depends(deps.get_db)
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not authorized',
        )
    
    product = crud.get_product_by_id(db, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Unable to find a product with the specified id',
        )
    
    # Check if user is an owner of this product
    if user.id != product.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Insufficient permissions',
        )

    updated_product = crud.put_product(db, product_id, product_put)

    if updated_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Unable to find a product with the specified id',
        )
    
    return updated_product


# Image and product image

@app.get('/images/{image_id}', response_model=schemas.ImageRead)
def get_image(image_id: int, db: Session = Depends(deps.get_db)):
    image = crud.get_image_by_id(db, image_id)
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Unable to find an image with the specified id',
        )
    return image


@app.post(
    '/images',
    response_model=schemas.ImageRead,
    status_code=status.HTTP_201_CREATED
)
def add_image(image: models.Image = Depends(deps.save_image)):
    return image


@app.post(
    '/products/{product_id}/addImage',
    response_model=schemas.ProductImageRead,
    status_code=status.HTTP_201_CREATED,
)
def add_product_image(
    product_id: int,
    image: schemas.ProductImageCreate,
    db: Session = Depends(deps.get_db),
):
    product = crud.get_product_by_id(db, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Unable to find a product with the specified id',
        )
    
    image = crud.get_image_by_id(db, image.image_id)

    if image is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Unable to find an image with the specified id',
        )
    
    try:
        product_image = crud.add_product_image(db, product, image)
    except sqlalchemy.exc.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Unable to add this image to the product',
        )

    return product_image
