import logging
from typing import List

from sqlalchemy.orm import Session

from . import exceptions
from .. import domain


logger = logging.getLogger(__name__)


class ProductRepository:
    """SQLAlchemy repository of product data"""
    session: Session


    def __init__(self, session: Session) -> None:
        self.session = session
    

    def get(self, product_id: int) -> domain.models.Product:
        queryset = self.session.query(domain.models.Product)
        queryset = queryset.filter_by(id=product_id)
        instance = queryset.first()

        if instance is None:
            raise exceptions.NotFoundError(
                f'Unable to find a product with id={product_id}',
            )

        return instance
    

    def add(self, product: domain.models.Product) -> domain.models.Product:
        self.session.add(product)
        return product
    

    def list(self, **filters) -> List[domain.models.Product]:
        product_set = self.session.query(domain.models.Product)

        if filters:
            product_set = product_set.filter_by(**filters)
        
        return product_set.all()
    

    def delete(self, product: domain.models.Product) -> None:
        self.session.delete(product)
