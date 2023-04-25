import logging
from typing import List
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session
from .. import crud
from .. import deps
from .. import models
from .. import schemas


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix='/productimages',
    tags=['productimages'],
)


@router.get('/', response_model=List[schemas.ProductImageRead])
def get_product_images(product_id: int, db: Session = Depends(deps.get_db)):
    """Returns list of product images filtered by specified product"""
    return crud.get_product_images(db, product_id)


@router.post(
    '/',
    response_model=schemas.ProductImageRead,
    status_code=status.HTTP_201_CREATED,
)
def add_product_image(
    product_image: schemas.ProductImageCreate,
    owner: models.User = Depends(deps.get_user),
    db: Session = Depends(deps.get_db),
):
    product_model = crud.get_product_by_id(db, product_image.product_id)

    if product_model is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Unable to find a product with id={product_image.product_id}',
        )

    if product_model.owner != owner:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='You are not the product owner',
        )

    image_model = crud.get_image_by_id(db, product_image.image_id)

    if image_model is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Unable to find an image with id={product_image.image_id}',
        )

    product_image_model = crud.add_product_image(
        db,
        product_model,
        image_model,
    )

    db.commit()

    if product_image_model is None:
        logger.error(
            'Failed adding product image. User: '
            f'{owner.username}, Product image: {product_image}'
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Unable to add product image',
        )
    
    return product_image_model


@router.get('/{product_image_id}', response_model=schemas.ProductImageRead)
def get_product_image(product_image_id: int, db: Session = Depends(deps.get_db)):
    product_image_model = crud.get_product_image_by_id(db, product_image_id)

    if product_image_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Unable to find a product image with id={product_image_id}',
        )

    return product_image_model


@router.delete('/{product_image_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_product_image(product_image_id: int, db: Session = Depends(deps.get_db)):
    product_image_model = crud.get_product_image_by_id(db, product_image_id)

    if product_image_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Unable to find a product image with id={product_image_id}',
        )
    
    crud.delete_product_image(db, product_image_id)
    db.commit()
