from typing import Optional
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy.orm import Session
from .. import models


def get_image_by_id(db: Session, image_id: int) -> Optional[models.Image]:
    """Returns image with the specified id"""
    query = select(models.Image).where(models.Image.id == image_id)
    return db.scalars(query).first()


def create_image(db: Session, image_path: str) -> models.Image:
    image = models.Image(image=image_path)
    db.add(image)
    db.commit()
    return image
