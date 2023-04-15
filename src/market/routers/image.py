from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session
from .. import crud
from .. import deps
from .. import models
from .. import schemas

router = APIRouter(
    prefix='/images',
    tags=['images'],
)


@router.get('/{image_id}', response_model=schemas.ImageRead)
def get_image(image_id: int, db: Session = Depends(deps.get_db)):
    """Returns information of specified image"""
    image = crud.get_image_by_id(db, image_id)
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Unable to find an image with the specified id',
        )
    return image


@router.post(
    '/',
    response_model=schemas.ImageRead,
    status_code=status.HTTP_201_CREATED
)
def add_image(image: models.Image = Depends(deps.save_image)):
    """Allows to upload an image"""
    return image
