import logging
import os
import os.path
import pydantic
import auth
import database
from uuid import uuid4
from fastapi import Body
from fastapi import Depends
from fastapi import HTTPException
from fastapi import UploadFile
from fastapi import security
from fastapi import status
from sqlalchemy.orm import Session
from database import crud
from database import models
from database import schemas


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


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


def get_user(
    token: str = Depends(auth.oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    user = auth.get_user(db, token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not authorized or your account is not active',
        )
    return user


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