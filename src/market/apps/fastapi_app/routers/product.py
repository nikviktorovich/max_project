import logging
from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session

import market.modules.user.domain.models
from market.apps.fastapi_app import deps
from market.modules.product import repositories
from market.modules.product import schemas
from market.modules.product.domain import models


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix='/products',
    tags=['products'],
)


@router.get('/', response_model=List[schemas.ProductRead])
def get_products(db: Session = Depends(deps.get_db)):
    """Returns a list of products"""
    repo = repositories.ProductRepository(db)
    return repo.list()


@router.post(
    '/',
    response_model=schemas.ProductRead,
    status_code=status.HTTP_201_CREATED,
)
def add_product(
    product_schema: schemas.ProductCreate,
    user: market.modules.user.domain.models.User = Depends(deps.get_user),
    db: Session = Depends(deps.get_db),
):
    """Adds a product"""
    repo = repositories.ProductRepository(db)
    instance = models.Product(
        title=product_schema.title,
        description=product_schema.description,
        is_active=product_schema.is_active,
        stock=product_schema.stock,
        price_rub=product_schema.price_rub,
        owner_id=user.id,
    )
    added_instance = repo.add(instance)
    db.commit()

    return added_instance


@router.get('/{product_id}', response_model=schemas.ProductRead)
def get_product(product_id: int, db: Session = Depends(deps.get_db)):
    """Returns information of specified product"""
    repo = repositories.ProductRepository(db)
    instance = repo.get(product_id)
    return instance


@router.put('/{product_id}', response_model=schemas.ProductRead)
def put_product(
    product_id: int,
    product_scheme: schemas.ProductPut,
    user: market.modules.user.domain.models.User = Depends(deps.get_user),
    db: Session = Depends(deps.get_db)
):
    """Allows to edit (PUT) specified product's info"""
    repo = repositories.ProductRepository(db)
    instance = repo.get(product_id)
    
    if user.id != instance.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not the product owner',
        )

    instance.title = product_scheme.title
    instance.description = product_scheme.description
    instance.stock = product_scheme.stock
    instance.price_rub = product_scheme.price_rub
    instance.is_active = product_scheme.is_active

    updated_instance = repo.add(instance)
    db.commit()

    return updated_instance


@router.delete('/{product_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    user: market.modules.user.domain.models.User = Depends(deps.get_user),
    db: Session = Depends(deps.get_db)
):
    """Deletes specified product"""
    repo = repositories.ProductRepository(db)
    instance = repo.get(product_id)

    if instance.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not the product owner',
        )
    
    repo.delete(instance)
    db.commit()
