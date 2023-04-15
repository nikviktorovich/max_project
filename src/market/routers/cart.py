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

router = APIRouter(
    prefix='/cart',
    tags=['cart'],
)


@router.get('/', response_model=List[schemas.CartItemRead])
def get_cart_items(
    user: models.User = Depends(deps.get_user),
    db: Session = Depends(deps.get_db),
):
    """Returns a list of authorized user's cart items"""
    return crud.get_cart_items(db, user.id)


@router.post(
    '/',
    response_model=schemas.CartItemRead,
    status_code=status.HTTP_201_CREATED
)
def add_cart_item(
    cart_item: schemas.CartItemCreate,
    user: models.User = Depends(deps.get_user),
    db: Session = Depends(deps.get_db),
):
    """Adds an item to authorized user's cart"""
    cart_item_internal = schemas.CartItemCreateInternal(
        **cart_item.dict(),
        user_id=user.id
    )
    added_item = crud.add_cart_item(db, cart_item_internal)
    
    if added_item is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Unable to add this product to your cart',
        )
    
    return added_item


@router.get('/{product_id}', response_model=schemas.CartItemRead)
def get_cart_item(
    product_id: int,
    user: models.User = Depends(deps.get_user),
    db: Session = Depends(deps.get_db),
):
    """Returns information about specified item in authorized user's cart"""
    return crud.get_cart_item(db, user.id, product_id)


@router.put('/{product_id}', response_model=schemas.CartItemRead)
def put_cart_item(
    product_id: int,
    cart_item: schemas.CartItemUpdate,
    user: models.User = Depends(deps.get_user),
    db: Session = Depends(deps.get_db),
):
    """Allows to edit (PUT) an item in authorized user's cart"""
    cart_item_internal = schemas.CartItemUpdateInternal(
        **cart_item.dict(),
        product_id=product_id,
        user_id=user.id,
    )
    updated_item = crud.put_cart_item(db, cart_item_internal)
    
    if updated_item is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Unable to update the item',
        )
    
    return updated_item


@router.delete('/{product_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_cart_item(
    product_id: int,
    user: models.User = Depends(deps.get_user),
    db: Session = Depends(deps.get_db),
):
    """Deletes specified item from authorized user's cart"""
    cart_item_internal = schemas.CartItemDelete(
        product_id=product_id,
        user_id=user.id,
    )

    crud.delete_cart_item(db, cart_item_internal)
    return
