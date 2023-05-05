from fastapi import APIRouter
from fastapi import Depends
from fastapi import status
from sqlalchemy.orm import Session
from .. import deps
from .. import domain
from .. import repositories
from .. import schemas

router = APIRouter(
    prefix='/images',
    tags=['images'],
)


@router.get('/{image_id}', response_model=schemas.ImageRead)
def get_image(image_id: int, db: Session = Depends(deps.get_db)):
    """Returns information of specified image"""
    repo = repositories.ImageRepository(db)
    instance = repo.get(image_id)
    return instance


@router.post(
    '/',
    response_model=schemas.ImageRead,
    status_code=status.HTTP_201_CREATED
)
def add_image(image: domain.models.Image = Depends(deps.save_image)):
    """Allows to upload an image"""
    return image