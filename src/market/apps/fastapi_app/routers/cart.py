from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session

import market.modules.user.domain.models
from market.apps.fastapi_app import deps
from market.modules.cart import repositories
from market.modules.cart import schemas
from market.modules.cart.domain import models

router = APIRouter(
    prefix='/cart',
    tags=['cart'],
)


@router.get('/', response_model=List[schemas.CartItemRead])
def get_cart_items(
    user: market.modules.user.domain.models.User = Depends(deps.get_user),
    db: Session = Depends(deps.get_db),
):
    """Returns a list of authorized user's cart items"""
    repo = repositories.CartRepository(db)
    instances = repo.list(user_id=user.id)
    return instances


@router.post(
    '/',
    response_model=schemas.CartItemRead,
    status_code=status.HTTP_201_CREATED
)
def add_cart_item(
    cart_item_schema: schemas.CartItemCreate,
    user: market.modules.user.domain.models.User = Depends(deps.get_user),
    db: Session = Depends(deps.get_db),
):
    """Adds an item to authorized user's cart"""
    cart_item = models.CartItem(
        amount=cart_item_schema.amount,
        user_id=user.id,
        product_id=cart_item_schema.product_id,
    )
    repo = repositories.CartRepository(db)

    product_id = cart_item_schema.product_id
    colliding_items = repo.list(user_id=user.id, product_id=product_id)
    if colliding_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'You already have a product with id={product_id} in cart',
        )

    added_cart_item = repo.add(cart_item)
    db.commit()
    
    return added_cart_item


@router.get('/{cart_item_id}', response_model=schemas.CartItemRead)
def get_cart_item(
    cart_item_id: int,
    user: market.modules.user.domain.models.User = Depends(deps.get_user),
    db: Session = Depends(deps.get_db),
):
    """Returns information about specified item in authorized user's cart"""
    repo = repositories.CartRepository(db)
    cart_item = repo.get(cart_item_id)

    if user.id != cart_item.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not an owner of this cart item',
        )

    return cart_item


@router.put('/{cart_item_id}', response_model=schemas.CartItemRead)
def put_cart_item(
    cart_item_id: int,
    cart_item_schema: schemas.CartItemUpdate,
    user: market.modules.user.domain.models.User = Depends(deps.get_user),
    db: Session = Depends(deps.get_db),
):
    """Allows to edit (PUT) an item in authorized user's cart"""
    repo = repositories.CartRepository(db)
    instance = repo.get(cart_item_id)

    if instance.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not an owner of this cart item',
        )

    instance.amount = cart_item_schema.amount
    instance.product_id = cart_item_schema.product_id

    updated_instance = repo.add(instance)
    db.commit()
    
    return updated_instance


@router.delete('/{cart_item_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_cart_item(
    cart_item_id: int,
    user: market.modules.user.domain.models.User = Depends(deps.get_user),
    db: Session = Depends(deps.get_db),
):
    """Deletes specified item from authorized user's cart"""
    repo = repositories.CartRepository(db)
    cart_item = repo.get(cart_item_id)
    
    if cart_item.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not the owner of this cart item',
        )
    
    repo.delete(cart_item)
    db.commit()
