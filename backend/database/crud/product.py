from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from .. import models
from .. import schemas


def get_products(db: Session, offset: int, limit: int) -> List[models.Product]:
    """Returns list of all products"""
    query = select(models.Product).limit(limit).offset(offset)
    return list(db.scalars(query).all())


def get_product_by_id(db: Session, product_id: int) -> Optional[models.Product]:
    """Returns product with the specified id"""
    query = select(models.Product).where(models.Product.id == product_id)
    return db.scalars(query).first()


def add_product(
    db: Session,
    product: schemas.ProductCreate,
    owner: models.User,
) -> Optional[models.Product]:
    product_model = models.Product(**product.dict(), owner=owner, images=[])
    db.add(product_model)
    db.commit()
    return product_model


def patch_product(
    db: Session,
    product_id: int,
    product: schemas.ProductUpdate
) -> Optional[models.Product]:
    """Updates instance's fields with new values from the schema"""
    product_model = get_product_by_id(db, product_id)

    if product_model is None:
        return None

    for key, value in product.dict(exclude_unset=True).items():
        setattr(product_model, key, value)
    
    db.commit()
    return product_model


def put_product(
    db: Session,
    product_id: int,
    product: schemas.ProductPut,
) -> Optional[models.Product]:
    product_model = get_product_by_id(db, product_id)

    if product_model is None:
        return None

    for key, value in product.dict().items():
        setattr(product_model, key, value)
    
    db.commit()
    return product_model


def get_product_image_by_id(
    db: Session,
    product_image_id: int
) -> Optional[models.ProductImage]:
    """Returns product image with the specified id"""
    query = select(models.ProductImage) \
        .where(models.ProductImage.id == product_image_id)
    return db.scalars(query).first()


def add_product_image(
    db: Session,
    product: models.Product,
    image: models.Image
) -> Optional[models.ProductImage]:
    product_image = models.ProductImage(
        product=product,
        image=image,
    )
    db.add(product_image)
    db.commit()
    return product_image
