import uuid

from fastapi import APIRouter
from fastapi import Depends
from fastapi import responses
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
    image_id: uuid.UUID,
    uow: unit_of_work.UnitOfWork = Depends(deps.get_uow),
):
    """Returns information of specified image"""
    instance = uow.images.get(image_id)
    return schemas.ImageRead.from_orm(instance)


@router.post('/', response_model=schemas.ImageRead)
def add_image(image: models.Image = Depends(deps.save_image)):
    """Allows to upload an image"""
    return responses.RedirectResponse(
        url=f'/images/{image.id}',
        status_code=status.HTTP_303_SEE_OTHER,
    )
