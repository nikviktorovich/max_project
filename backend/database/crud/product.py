from typing import List, Optional
from sqlalchemy.orm import Session
from .. import models


def get_products(db: Session, offset: int, limit: int) -> List[models.Product]:
    query = db.query(models.Product).offset(offset).limit(limit)
    return query.all()


def get_product_by_id(db: Session, product_id: int) -> Optional[models.Product]:
    query = db.query(models.Product).filter_by(id=product_id)
    return query.first()


def get_product_image_by_id(
    db: Session,
    product_image_id: int
) -> Optional[models.ProductImage]:
    query = db.query(models.ProductImage).filter_by(id=product_image_id)
    return query.first()
