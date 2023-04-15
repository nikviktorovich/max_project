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
    prefix='/products',
    tags=['products'],
)


@router.get('/', response_model=List[schemas.ProductRead])
def get_products(
    offset: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db)
):
    """Returns a list of products"""
    return crud.get_products(db, offset, limit)


@router.post(
    '/',
    response_model=schemas.ProductRead,
    status_code=status.HTTP_201_CREATED,
)
def add_product(
    product: schemas.ProductCreate,
    owner: models.User = Depends(deps.get_user),
    db: Session = Depends(deps.get_db),
):
    """Adds a product"""
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


@router.get('/{product_id}', response_model=schemas.ProductRead)
def get_product(product_id: int, db: Session = Depends(deps.get_db)):
    """Returns information of specified product"""
    product_model = crud.get_product_by_id(db, product_id)
    if product_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Unable to find a product with the specified id',
        )
    return product_model


@router.patch('/{product_id}', response_model=schemas.ProductRead)
def patch_product(
    product_id: int,
    product_patch: schemas.ProductUpdate,
    user: models.User = Depends(deps.get_user),
    db: Session = Depends(deps.get_db)
):
    """Allows to edit (PATCH) specified product's info"""
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


@router.put('/{product_id}', response_model=schemas.ProductRead)
def put_product(
    product_id: int,
    product_put: schemas.ProductPut,
    user: models.User = Depends(deps.get_user),
    db: Session = Depends(deps.get_db)
):
    """Allows to edit (PUT) specified product's info"""
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


@router.delete('/{product_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    user: models.User = Depends(deps.get_user),
    db: Session = Depends(deps.get_db)
):
    """Deletes specified product"""
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
