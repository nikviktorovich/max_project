from typing import List
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from .. import models
from .. import schemas


def get_product_images(
    db: Session,
    product_id: int,
) -> List[models.ProductImage]:
    query = select(models.ProductImage).filter(
        models.ProductImage.product_id == product_id,
    )
    return list(db.scalars(query).all())


def get_product_image_by_id(
    db: Session,
    product_image_id: int,
) -> Optional[models.ProductImage]:
    """Returns product image with the specified id"""
    query = select(models.ProductImage).where(
        models.ProductImage.id == product_image_id,
    )
    return db.scalars(query).first()


def add_product_image(
    db: Session,
    product: models.Product,
    image: models.Image,
) -> Optional[models.ProductImage]:
    product_image = models.ProductImage(
        product=product,
        image=image,
    )
    db.add(product_image)
    return product_image


def delete_product_image(db: Session, product_image_id: int) -> None:
    query = select(models.ProductImage).filter(
        models.ProductImage.id == product_image_id,
    )
    product_image_model = db.query(query).first()
    db.delete(product_image_model)
