import uuid
from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import responses
from fastapi import status

import market.modules.user.domain.models
from market.apps.fastapi_app import deps
from market.apps.fastapi_app.routers.cart import schemas
from market.modules.cart.domain import models
from market.services import unit_of_work

router = APIRouter(
    prefix='/cart',
    tags=['cart'],
)


@router.get('/', response_model=List[schemas.CartItemRead])
def get_cart_items(
    user: market.modules.user.domain.models.User = Depends(deps.get_user),
    uow: unit_of_work.UnitOfWork = Depends(deps.get_uow),
):
    """Returns a list of authorized user's cart items"""
    instances = uow.cart.list(user_id=user.id)
    return [schemas.CartItemRead.from_orm(instance) for instance in instances]


@router.post('/', response_model=schemas.CartItemRead)
def add_cart_item(
    cart_item_schema: schemas.CartItemCreate,
    user: market.modules.user.domain.models.User = Depends(deps.get_user),
    uow: unit_of_work.UnitOfWork = Depends(deps.get_uow),
):
    """Adds an item to authorized user's cart"""
    cart_item_id = uuid.uuid4()
    cart_item = models.CartItem(
        id=cart_item_id,
        amount=cart_item_schema.amount,
        user_id=user.id,
        product_id=cart_item_schema.product_id,
    )

    colliding_items = uow.cart.list(
        user_id=cart_item.user_id,
        product_id=cart_item.product_id,
    )

    if colliding_items:
        product_id = cart_item_schema.product_id
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'You already have a product with id={product_id} in cart',
        )

    added_cart_item = uow.cart.add(cart_item)
    uow.commit()

    return responses.RedirectResponse(
        url=f'/cart/{cart_item_id}',
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get('/{cart_item_id}', response_model=schemas.CartItemRead)
def get_cart_item(
    cart_item_id: uuid.UUID,
    user: market.modules.user.domain.models.User = Depends(deps.get_user),
    uow: unit_of_work.UnitOfWork = Depends(deps.get_uow),
):
    """Returns information about specified item in authorized user's cart"""
    cart_item = uow.cart.get(cart_item_id)

    if user.id != cart_item.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not an owner of this cart item',
        )

    return schemas.CartItemRead.from_orm(cart_item)


@router.put('/{cart_item_id}', response_model=schemas.CartItemRead)
def put_cart_item(
    cart_item_id: uuid.UUID,
    cart_item_schema: schemas.CartItemUpdate,
    user: market.modules.user.domain.models.User = Depends(deps.get_user),
    uow: unit_of_work.UnitOfWork = Depends(deps.get_uow),
):
    """Allows to edit (PUT) an item in authorized user's cart"""
    instance = uow.cart.get(cart_item_id)

    if instance.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not an owner of this cart item',
        )

    updated_instance = uow.cart.update(
        instance,
        amount = cart_item_schema.amount,
        product_id = cart_item_schema.product_id,
    )
    uow.commit()
    
    return responses.RedirectResponse(
        url=f'/cart/{cart_item_id}',
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.delete('/{cart_item_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_cart_item(
    cart_item_id: uuid.UUID,
    user: market.modules.user.domain.models.User = Depends(deps.get_user),
    uow: unit_of_work.UnitOfWork = Depends(deps.get_uow),
):
    """Deletes specified item from authorized user's cart"""
    cart_item = uow.cart.get(cart_item_id)
    
    if cart_item.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not the owner of this cart item',
        )
    
    uow.cart.delete(cart_item)
    uow.commit()
