from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from .. import models


def get_products(db: Session, offset: int, limit: int) -> List[models.Product]:
    """Returns list of all products"""
    query = select(models.Product).limit(limit).offset(offset)
    return list(db.scalars(query).all())


def get_product_by_id(db: Session, product_id: int) -> Optional[models.Product]:
    """Returns product with the specified id"""
    query = select(models.Product).where(models.Product.id == product_id)
    return db.scalars(query).first()


def get_product_image_by_id(
    db: Session,
    product_image_id: int
) -> Optional[models.ProductImage]:
    """Returns product image with the specified id"""
    query = select(models.ProductImage) \
        .where(models.ProductImage.id == product_image_id)
    return db.scalars(query).first()
