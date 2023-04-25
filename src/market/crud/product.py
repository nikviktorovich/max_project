from typing import List, Optional
from sqlalchemy import delete
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


def _make_product_images(
    db: Session,
    image_ids: List[int]
) -> List[models.ProductImage]:
    """Converts images to product images, which can be added to a product"""
    images_query = select(models.Image).where(models.Image.id.in_(image_ids))
    image_models = db.scalars(images_query)

    product_images = []
    for image_model in image_models:
        product_image_model = models.ProductImage(
            image=image_model
        )
        product_images.append(product_image_model)
    return product_images


def _delete_product_images(db: Session, product: models.Product) -> None:
    remove_images_query = delete(models.ProductImage).where(
        models.ProductImage.product == product
    )
    db.execute(remove_images_query)


def _check_images_collision(db: Session, image_ids: List[int]) -> None:
    query = select(models.ProductImage).where(
        models.ProductImage.image_id.in_(image_ids)
    )
    existing_product_images = db.scalars(query).all()

    if existing_product_images:
        raise ValueError('Some of the images are already bound to a product')


def add_product(
    db: Session,
    product: schemas.ProductCreate,
    owner: models.User,
) -> Optional[models.Product]:
    product_dict = product.dict()
    product_model = models.Product(**product_dict, owner=owner)

    db.add(product_model)
    db.commit()

    return product_model


def patch_product(
    db: Session,
    product_id: int,
    product: schemas.ProductUpdate
) -> Optional[models.Product]:
    """Updates instance's fields with new values from the schema"""
    product_dict = product.dict(exclude_unset=True)
    product_model = get_product_by_id(db, product_id)

    if product_model is None:
        return None

    for key, value in product_dict.items():
        setattr(product_model, key, value)
    
    db.commit()
    return product_model


def put_product(
    db: Session,
    product_id: int,
    product: schemas.ProductPut,
) -> Optional[models.Product]:
    product_dict = product.dict()
    product_model = get_product_by_id(db, product_id)

    if product_model is None:
        return None

    for key, value in product_dict.items():
        setattr(product_model, key, value)
    
    db.commit()
    return product_model


def delete_product(db: Session, product_id: int) -> None:
    query = delete(models.Product).where(models.Product.id == product_id)
    db.execute(query)
    db.commit()
