import logging
import uuid
from typing import List

from sqlalchemy.orm import Session

import market.common.errors
from market.modules.cart.domain import models


logger = logging.getLogger(__name__)


class CartRepository:
    """SQLAlchemy repository of user cart data"""
    session: Session


    def __init__(self, session: Session) -> None:
        self.session = session
    

    def get(self, cart_item_id: uuid.UUID) -> models.CartItem:
        queryset = self.session.query(models.CartItem)
        queryset = queryset.filter_by(id=cart_item_id)
        instance = queryset.first()

        if instance is None:
            raise market.common.errors.NotFoundError(
                f'Unable to find a cart item with id={cart_item_id}',
            )

        return instance
    

    def add(self, cart_item: models.CartItem) -> models.CartItem:
        self.session.add(cart_item)
        return cart_item
    

    def list(self, **filters) -> List[models.CartItem]:
        cart_item_set = self.session.query(models.CartItem)

        if filters:
            cart_item_set = cart_item_set.filter_by(**filters)
        
        return cart_item_set.all()
    

    def delete(self, cart_item: models.CartItem) -> None:
        self.session.delete(cart_item)

