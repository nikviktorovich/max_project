from fastapi import APIRouter
from fastapi import Depends
from fastapi import status

from market.apps.fastapi_app import deps
from market.modules.image.domain import models
from market.modules.image import schemas
from market.services import unit_of_work

router = APIRouter(
    prefix='/images',
    tags=['images'],
)


@router.get('/{image_id}', response_model=schemas.ImageRead)
def get_image(
    image_id: int,
    uow: unit_of_work.UnitOfWork = Depends(deps.get_uow),
):
    """Returns information of specified image"""
    instance = uow.images.get(image_id)
    return schemas.ImageRead.from_orm(instance)


@router.post(
    '/',
    response_model=schemas.ImageRead,
    status_code=status.HTTP_201_CREATED
)
def add_image(image: models.Image = Depends(deps.save_image)):
    """Allows to upload an image"""
    return schemas.ImageRead.from_orm(image)
