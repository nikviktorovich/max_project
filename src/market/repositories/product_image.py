import logging
from typing import List
from sqlalchemy.orm import Session
from . import exceptions
from .. import domain


logger = logging.getLogger(__name__)


class ProductImageRepository:
    """SQLAlchemy repository of product image data"""
    session: Session


    def __init__(self, session: Session) -> None:
        self.session = session
    

    def get(self, product_image_id: int) -> domain.models.ProductImage:
        queryset = self.session.query(domain.models.ProductImage)
        queryset = queryset.filter_by(id=product_image_id)
        instance = queryset.first()

        if instance is None:
            raise exceptions.NotFoundError(
                f'Unable to find a product image with id={product_image_id}',
            )

        return instance
    

    def add(
        self,
        product_image: domain.models.ProductImage,
    ) -> domain.models.ProductImage:
        self.session.add(product_image)
        return product_image
    

    def list(self, **filters) -> List[domain.models.ProductImage]:
        product_image_set = self.session.query(domain.models.ProductImage)

        if filters:
            product_image_set = product_image_set.filter_by(**filters)
        
        return product_image_set.all()
    

    def delete(self, product_image: domain.models.ProductImage) -> None:
        self.session.delete(product_image)
