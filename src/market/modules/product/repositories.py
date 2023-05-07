import logging
from typing import List

from sqlalchemy.orm import Session

import market.common.errors
from market.modules.product.domain import models


logger = logging.getLogger(__name__)


class ProductRepository:
    """SQLAlchemy repository of product data"""
    session: Session


    def __init__(self, session: Session) -> None:
        self.session = session
    

    def get(self, product_id: int) -> models.Product:
        queryset = self.session.query(models.Product)
        queryset = queryset.filter_by(id=product_id)
        instance = queryset.first()

        if instance is None:
            raise market.common.errors.NotFoundError(
                f'Unable to find a product with id={product_id}',
            )

        return instance
    

    def add(self, product: models.Product) -> models.Product:
        self.session.add(product)
        return product
    

    def list(self, **filters) -> List[models.Product]:
        product_set = self.session.query(models.Product)

        if filters:
            product_set = product_set.filter_by(**filters)
        
        return product_set.all()
    

    def delete(self, product: models.Product) -> None:
        self.session.delete(product)
