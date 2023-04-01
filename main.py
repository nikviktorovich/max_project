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
from fastapi import responses
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


@app.exception_handler(Exception)
def global_exception_handler(request, exception):
    message = f"Failed to execute: {request.method}: {request.url}. Error: {exception}"
    logger.error(message)
    return responses.JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={'detail': 'Server error'}
    )


@app.exception_handler(ValueError)
def value_error_handler(request, exception):
    return responses.JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': str(exception)},
    )


# Routes

# Auth

@app.post('/token', response_model=schemas.Token)
async def login(
    form_data: security.OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(deps.get_db),
):
    """Authorizes user and returns an access token."""
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

@app.get('/user', response_model=schemas.UserRead)
def get_user(
    user: models.User = Depends(deps.get_user),
    db: Session = Depends(deps.get_db),
):
    return user


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


@app.delete('/products/{product_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    user: models.User = Depends(deps.get_user),
    db: Session = Depends(deps.get_db)
):
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
    
    crud.delete_product(db, product_id)
    return


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


@app.get('/cart', response_model=List[schemas.CartItemRead])
def get_cart_items(
    user: models.User = Depends(deps.get_user),
    db: Session = Depends(deps.get_db),
):
    return crud.get_cart_items(db, user.id)


@app.post(
    '/cart',
    response_model=schemas.CartItemRead,
    status_code=status.HTTP_201_CREATED
)
def add_cart_item(
    cart_item: schemas.CartItemCreate,
    user: models.User = Depends(deps.get_user),
    db: Session = Depends(deps.get_db),
):
    cart_item_internal = schemas.CartItemCreateInternal(
        **cart_item.dict(),
        user_id=user.id
    )
    added_item = crud.add_cart_item(db, cart_item_internal)
    
    if added_item is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Unable to add this product to your cart',
        )
    
    return added_item


@app.get('/cart/{product_id}', response_model=schemas.CartItemRead)
def get_cart_item(
    product_id: int,
    user: models.User = Depends(deps.get_user),
    db: Session = Depends(deps.get_db),
):
    return crud.get_cart_item(db, user.id, product_id)


@app.put('/cart/{product_id}', response_model=schemas.CartItemRead)
def put_cart_item(
    product_id: int,
    cart_item: schemas.CartItemUpdate,
    user: models.User = Depends(deps.get_user),
    db: Session = Depends(deps.get_db),
):
    cart_item_internal = schemas.CartItemUpdateInternal(
        **cart_item.dict(),
        product_id=product_id,
        user_id=user.id,
    )
    updated_item = crud.put_cart_item(db, cart_item_internal)
    
    if updated_item is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Unable to update the item',
        )
    
    return updated_item


@app.delete('/cart/{product_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_cart_item(
    product_id: int,
    user: models.User = Depends(deps.get_user),
    db: Session = Depends(deps.get_db),
):
    cart_item_internal = schemas.CartItemDelete(
        product_id=product_id,
        user_id=user.id,
    )

    crud.delete_cart_item(db, cart_item_internal)
    return
