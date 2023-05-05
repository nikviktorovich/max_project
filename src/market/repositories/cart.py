import logging
from typing import List

from sqlalchemy.orm import Session

from . import exceptions
from .. import domain


logger = logging.getLogger(__name__)


class CartRepository:
    """SQLAlchemy repository of user cart data"""
    session: Session


    def __init__(self, session: Session) -> None:
        self.session = session
    

    def get(self, cart_item_id: int) -> domain.models.CartItem:
        queryset = self.session.query(domain.models.CartItem)
        queryset = queryset.filter_by(id=cart_item_id)
        instance = queryset.first()

        if instance is None:
            raise exceptions.NotFoundError(
                f'Unable to find a cart item with id={cart_item_id}',
            )

        return instance
    

    def add(self, cart_item: domain.models.CartItem) -> domain.models.CartItem:
        self.session.add(cart_item)
        return cart_item
    

    def list(self, **filters) -> List[domain.models.CartItem]:
        cart_item_set = self.session.query(domain.models.CartItem)

        if filters:
            cart_item_set = cart_item_set.filter_by(**filters)
        
        return cart_item_set.all()
    

    def delete(self, cart_item: domain.models.CartItem) -> None:
        self.session.delete(cart_item)
