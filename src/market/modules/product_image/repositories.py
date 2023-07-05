import logging
import uuid
from typing import List

from sqlalchemy.orm import Session

import market.common.errors
from market.modules.product_image.domain import models


logger = logging.getLogger(__name__)


class ProductImageRepository:
    """SQLAlchemy repository of product image data"""
    session: Session


    def __init__(self, session: Session) -> None:
        self.session = session
    

    def get(self, product_image_id: uuid.UUID) -> models.ProductImage:
        queryset = self.session.query(models.ProductImage)
        queryset = queryset.filter_by(id=product_image_id)
        instance = queryset.first()

        if instance is None:
            raise market.common.errors.NotFoundError(
                f'Unable to find a product image with id={product_image_id}',
            )

        return instance
    

    def add(
        self,
        product_image: models.ProductImage,
    ) -> models.ProductImage:
        self.session.add(product_image)
        return product_image
    

    def list(self, **filters) -> List[models.ProductImage]:
        product_image_set = self.session.query(models.ProductImage)

        if filters:
            product_image_set = product_image_set.filter_by(**filters)
        
        return product_image_set.all()
    

    def delete(self, product_image: models.ProductImage) -> None:
        self.session.delete(product_image)
    

    def update(
        self,
        product_image: models.ProductImage,
        **fields,
    ) -> models.ProductImage:
        for attribute, value in fields.items():
            setattr(product_image, attribute, value)
        
        return product_image
