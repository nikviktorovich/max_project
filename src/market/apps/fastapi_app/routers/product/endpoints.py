import logging
import uuid
from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import responses
from fastapi import status

import market.modules.user.domain.models
from market.apps.fastapi_app import deps
from market.apps.fastapi_app.routers.product import schemas
from market.modules.product.domain import models
from market.services import unit_of_work


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix='/products',
    tags=['products'],
)


@router.get('/', response_model=List[schemas.ProductRead])
def get_products(uow: unit_of_work.UnitOfWork = Depends(deps.get_uow)):
    """Returns a list of products"""
    instances = uow.products.list()
    return [schemas.ProductRead.from_orm(instance) for instance in instances]


@router.post('/', response_model=schemas.ProductRead)
def add_product(
    product_schema: schemas.ProductCreate,
    user: market.modules.user.domain.models.User = Depends(deps.get_user),
    uow: unit_of_work.UnitOfWork = Depends(deps.get_uow),
):
    """Adds a product"""
    product_id = uuid.uuid4()
    instance = models.Product(
        id=product_id,
        title=product_schema.title,
        description=product_schema.description,
        is_active=product_schema.is_active,
        stock=product_schema.stock,
        price_rub=product_schema.price_rub,
        owner_id=user.id,
    )
    added_instance = uow.products.add(instance)
    uow.commit()

    return responses.RedirectResponse(
        url=f'/products/{product_id}',
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get('/{product_id}', response_model=schemas.ProductRead)
def get_product(
    product_id: uuid.UUID,
    uow: unit_of_work.UnitOfWork = Depends(deps.get_uow),
):
    """Returns information of specified product"""
    instance = uow.products.get(product_id)
    return schemas.ProductRead.from_orm(instance)


@router.put('/{product_id}', response_model=schemas.ProductRead)
def put_product(
    product_id: uuid.UUID,
    product_scheme: schemas.ProductPut,
    user: market.modules.user.domain.models.User = Depends(deps.get_user),
    uow: unit_of_work.UnitOfWork = Depends(deps.get_uow),
):
    """Allows to edit (PUT) specified product's info"""
    instance = uow.products.get(product_id)
    
    if user.id != instance.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not the product owner',
        )

    updated_instance = uow.products.update(
        instance,
        title = product_scheme.title,
        description = product_scheme.description,
        stock = product_scheme.stock,
        price_rub = product_scheme.price_rub,
        is_active = product_scheme.is_active,
    )
    uow.commit()

    return responses.RedirectResponse(
        url=f'/products/{product_id}',
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.delete('/{product_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: uuid.UUID,
    user: market.modules.user.domain.models.User = Depends(deps.get_user),
    uow: unit_of_work.UnitOfWork = Depends(deps.get_uow),
):
    """Deletes specified product"""
    instance = uow.products.get(product_id)

    if instance.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not the product owner',
        )
    
    uow.products.delete(instance)
    uow.commit()
