import logging
import os
import os.path
import fastapi.exceptions
import pydantic
import sqlalchemy.exc
import auth
import database
from typing import List, Optional
from uuid import uuid4
from fastapi import Body
from fastapi import Depends
from fastapi import FastAPI
from fastapi import File
from fastapi import Form
from fastapi import HTTPException
from fastapi import UploadFile
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

oauth2_scheme = security.OAuth2PasswordBearer(tokenUrl='token')

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


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Routes
@app.get('/')
async def get_index(token: str = Depends(oauth2_scheme)):
    return {'token': token}


@app.post('/token')
async def login(
    form_data: security.OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
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


def get_user_create_form_data(
    username: str = Body(),
    password: str = Body(),
    full_name: str = Body(default=''),
) -> schemas.UserCreate:
    try:
        return schemas.UserCreate(
            username=username,
            full_name=full_name,
            password=password
        )
    except pydantic.ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.errors()
        )


def register_user(
    user_data: schemas.UserCreate = Depends(get_user_create_form_data),
    form_data: security.OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    try:
        token = auth.register_user(db, user_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    else:
        return token


@app.post('/signup')
async def signup(token: schemas.Token = Depends(register_user)):
    """
    """
    
    return token


@app.get('/products', response_model=List[schemas.ProductRead])
def get_products(
    offset: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud.get_products(db, offset, limit)


def get_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    user = auth.get_user(db, token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not authorized or your account is not active',
        )
    return user

@app.get('/images/{image_id}', response_model=schemas.ImageRead)
def get_image(image_id: int, db: Session = Depends(get_db)):
    image = crud.get_image_by_id(db, image_id)
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Unable to find an image with the specified id',
        )
    return image


def get_available_media_filename(media_path: str, media_filename: str) -> str:
    """Checks if media file name is available and returns the original
    file name if it is and generates a unique one otherwise

    Returns:
        Available media file name
    """
    new_media_filename = media_filename

    while os.path.exists(os.path.join(media_path, new_media_filename)):
        new_media_filename = f'{uuid4().hex}_{media_filename}'
    
    return new_media_filename


def write_image(image_file: UploadFile) -> str:
    """Writes uploaded image into a file in a media folder"""
    media_path = os.getenv('MEDIA_PATH')
    
    if media_path is None:
        raise RuntimeError('MEDIA_PATH is not specified')
    
    # We need image to name to at least have an information
    # about it's extension
    if image_file.filename is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Image name is not specified',
        )
    
    # Saving image into media folder
    image_filename = get_available_media_filename(media_path, image_file.filename)
    image_path = os.path.join(media_path, image_filename)
    try:
        image_contents = image_file.file.read()
        with open(image_path, 'wb') as f:
            f.write(image_contents)
    except IOError as e:
        logging.error(f'Error adding an image: {str(e)} (filename: {e.filename})')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Unable to add the image',
        )
    return image_filename


def save_image(
    image_filename: str = Depends(write_image),
    db: Session = Depends(get_db)
) -> models.Image:
    image = crud.create_image(db, image_filename)
    return image

@app.post(
    '/images',
    response_model=schemas.ImageRead,
    status_code=status.HTTP_201_CREATED
)
def add_image(image: models.Image = Depends(save_image)):
    return image


@app.post(
    '/products/{product_id}/addImage',
    response_model=schemas.ProductImageRead,
    status_code=status.HTTP_201_CREATED,
)
def add_product_image(
    product_id: int,
    image: schemas.ProductImageCreate,
    db: Session = Depends(get_db),
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
