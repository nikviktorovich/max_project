from typing import Optional
from sqlalchemy.orm import Session
from .. import models


def get_image_by_id(db: Session, image_id: int) -> Optional[models.Image]:
    """Returns image with the specified id
    
    Raises:
        MultipleResultsFound:
    """
    return db.query(models.Image).filter_by(id=image_id).one_or_none()
