import logging
from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session

import market.modules.user.domain.models
import market.modules.product.repositories
import market.modules.image.repositories
from market.apps.fastapi_app import deps
from market.modules.product_image import repositories
from market.modules.product_image import schemas
from market.modules.product_image.domain import models


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix='/productimages',
    tags=['productimages'],
)


@router.get('/', response_model=List[schemas.ProductImageRead])
def get_product_images(product_id: int, db: Session = Depends(deps.get_db)):
    """Returns list of product images filtered by specified product"""
    repo = repositories.ProductImageRepository(db)
    instances = repo.list(product_id=product_id)
    return instances


@router.post(
    '/',
    response_model=schemas.ProductImageRead,
    status_code=status.HTTP_201_CREATED,
)
def add_product_image(
    product_image_schema: schemas.ProductImageCreate,
    user: market.modules.user.domain.models.User = Depends(deps.get_user),
    db: Session = Depends(deps.get_db),
):
    product_repo = market.modules.product.repositories.ProductRepository(db)
    product_instance = product_repo.get(product_image_schema.product_id)

    if product_instance.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='You are not the product owner',
        )
    
    # To raise exception in case if image does not exist
    image_repo = market.modules.image.repositories.ImageRepository(db)
    _ = image_repo.get(product_image_schema.image_id)
    
    product_image_repo = repositories.ProductImageRepository(db)
    product_image_instance = models.ProductImage(
        product_id=product_image_schema.product_id,
        image_id=product_image_schema.image_id,
    )
    product_image_repo.add(product_image_instance)

    db.commit()
    
    return product_image_instance


@router.get('/{product_image_id}', response_model=schemas.ProductImageRead)
def get_product_image(product_image_id: int, db: Session = Depends(deps.get_db)):
    repo = repositories.ProductImageRepository(db)
    instance = repo.get(product_image_id)
    return instance


@router.delete('/{product_image_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_product_image(
    product_image_id: int,
    user: market.modules.user.domain.models.User = Depends(deps.get_user),
    db: Session = Depends(deps.get_db)
):
    product_image_repo = repositories.ProductImageRepository(db)
    product_image_instance = product_image_repo.get(product_image_id)

    product_repo = market.modules.product.repositories.ProductRepository(db)
    product_instance = product_repo.get(product_image_instance.product_id)

    if product_instance.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not the product owner',
        )

    db.commit()
