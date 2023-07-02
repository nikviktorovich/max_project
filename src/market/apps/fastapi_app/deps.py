import logging
import os
import os.path
import uuid
from typing import Iterator

import pydantic
from fastapi import Body
from fastapi import Depends
from fastapi import HTTPException
from fastapi import UploadFile
from fastapi import security
from fastapi import status

import market.database
import market.database.orm
import market.services.auth
import market.modules.image.domain.models
import market.modules.image.repositories
import market.modules.user.domain.models
import market.modules.user.repositories
import market.modules.user.schemas
from market.services import unit_of_work
from market.apps.fastapi_app import auth


def get_uow() -> Iterator[unit_of_work.abstract.UnitOfWork]:
    uow = unit_of_work.sqlalchemy.SQLAlchemyUnitOfWork(
        market.database.orm.DEFAULT_SESSION_FACTORY,
    )
    with uow:
        yield uow


def get_user_create_form_data(
    form_data: security.OAuth2PasswordRequestForm = Depends(),
    full_name: str = Body(default=''),
) -> market.modules.user.schemas.UserCreate:
    try:
        return market.modules.user.schemas.UserCreate(
            username=form_data.username,
            password=form_data.password,
            full_name=full_name,
        )
    except pydantic.ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.errors()
        )


def get_user(
    token: str = Depends(auth.oauth2_scheme),
    uow: unit_of_work.UnitOfWork = Depends(get_uow),
) -> market.modules.user.domain.models.User:
    auth_service = market.services.auth.AuthServiceImpl(uow.users)
    user = auth_service.get_user(token)

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
        new_media_filename = f'{uuid.uuid4().hex}_{media_filename}'
    
    return new_media_filename


def write_image(image: UploadFile) -> str:
    """Writes uploaded image into a file in a media folder"""
    media_path = os.getenv('MEDIA_PATH')
    
    if media_path is None:
        raise RuntimeError('MEDIA_PATH is not specified')
    
    # We need image to name to at least have an information
    # about it's extension
    if image.filename is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Image name is not specified',
        )
    
    # Saving image into media folder
    image_filename = get_available_media_filename(media_path, image.filename)
    image_path = os.path.join(media_path, image_filename)
    try:
        image_contents = image.file.read()
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
    uow: unit_of_work.UnitOfWork = Depends(get_uow),
) -> market.modules.image.domain.models.Image:
    instance = market.modules.image.domain.models.Image(
        id=uuid.uuid4(),
        image=image_filename,
    )
    added_instance = uow.images.add(instance)
    uow.commit()
    return added_instance
