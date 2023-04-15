import sqlalchemy.exc
from typing import List
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.sql import delete
from sqlalchemy.sql import select
from .. import models
from .. import schemas


def get_cart_item(
    db: Session,
    user_id: int,
    product_id: int
) -> Optional[models.CartItem]:
    query = select(models.CartItem).where(
        models.CartItem.user_id == user_id,
        models.CartItem.product_id == product_id,
    )
    return db.execute(query).scalar()


def get_cart_items(db: Session, user_id: int) -> List[models.CartItem]:
    query = select(models.CartItem).where(models.CartItem.user_id == user_id)
    return list(db.scalars(query).all())


def add_cart_item(
    db: Session,
    item: schemas.CartItemCreateInternal,
) -> Optional[models.CartItem]:
    item_model = models.CartItem(**item.dict())
    try:
        db.add(item_model)
        db.commit()
    except sqlalchemy.exc.IntegrityError:
        return None
    return item_model


def put_cart_item(
    db: Session,
    item: schemas.CartItemUpdateInternal
) -> Optional[models.CartItem]:
    item_model = get_cart_item(db, item.user_id, item.product_id)
    
    if item_model is None:
        return None
    
    for key, value in item.dict().items():
        setattr(item_model, key, value)
    
    db.commit()
    return item_model


def delete_cart_item(db: Session, item: schemas.CartItemDelete) -> None:
    query = delete(models.CartItem).where(
        models.CartItem.user_id == item.user_id,
        models.CartItem.product_id == item.product_id,
    )
    db.execute(query)
    db.commit()
