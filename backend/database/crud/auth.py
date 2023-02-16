from typing import Optional
from sqlalchemy.orm import Session
from .. import models


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Returns User by user id or None if not found
    
    Raises:
        MultipleResultsFound: If more than one user found with the specified id
    """
    return db.query(models.User).filter(models.User.id == user_id).one_or_none()


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Returns User by username or None if not found
    
    Raises:
        MultipleResultsFound: If more than one user found with the username
    """
    return db.query(models.User).filter_by(username=username).one_or_none()


def is_username_available(db: Session, username: str) -> bool:
    return db.query(models.User).filter_by(username=username).first() is None
