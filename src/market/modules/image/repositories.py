import logging
from typing import List

from sqlalchemy.orm import Session

import market.common.errors
from market.modules.image.domain import models


logger = logging.getLogger(__name__)


class ImageRepository:
    """SQLAlchemy repository of image data"""
    session: Session


    def __init__(self, session: Session) -> None:
        self.session = session
    

    def get(self, image_id: int) -> models.Image:
        queryset = self.session.query(models.Image)
        queryset = queryset.filter_by(id=image_id)
        instance = queryset.first()

        if instance is None:
            raise market.common.errors.NotFoundError(
                f'Unable to find an image with id={image_id}',
            )

        return instance
    

    def add(self, image: models.Image) -> models.Image:
        self.session.add(image)
        return image
    

    def list(self, **filters) -> List[models.Image]:
        image_set = self.session.query(models.Image)

        if filters:
            image_set = image_set.filter_by(**filters)
        
        return image_set.all()
    

    def delete(self, image: models.Image) -> None:
        self.session.delete(image)
