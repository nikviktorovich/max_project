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
    prev_images = product.images
    prev_image_ids = [prev_image.id for prev_image in prev_images]
    remove_images_query = delete(models.ProductImage).where(
        models.ProductImage.id.in_(prev_image_ids)
    )
    db.execute(remove_images_query)


def add_product(
    db: Session,
    product: schemas.ProductCreate,
    owner: models.User,
) -> Optional[models.Product]:
    product_dict = product.dict()
    product_dict['images'] = []

    product_model = models.Product(**product_dict, owner=owner)

    if product.images:
        image_ids = [image.image_id for image in product.images]
        product_model.images = _make_product_images(db, image_ids)

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
    
    if 'images' in product_dict:
        del product_dict['images']

    product_model = get_product_by_id(db, product_id)

    if product_model is None:
        return None

    for key, value in product_dict.items():
        setattr(product_model, key, value)
    
    if product.images:
        _delete_product_images(db, product_model)
        image_ids = [image.image_id for image in product.images]
        product_model.images = _make_product_images(db, image_ids)
    
    db.commit()
    return product_model


def put_product(
    db: Session,
    product_id: int,
    product: schemas.ProductPut,
) -> Optional[models.Product]:
    product_dict = product.dict()
    product_dict['images'] = []

    product_model = get_product_by_id(db, product_id)

    if product_model is None:
        return None

    for key, value in product.dict().items():
        setattr(product_model, key, value)
    
    if product.images:
        _delete_product_images(db, product_model)
        image_ids = [image.image_id for image in product.images]
        product_model.images = _make_product_images(db, image_ids)
    
    db.commit()
    return product_model


def delete_product(db: Session, product_id: int) -> None:
    query = delete(models.Product).where(models.Product.id == product_id)
    db.execute(query)
    db.commit()


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
