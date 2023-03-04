from typing import Optional
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import Session
from .. import models
from .. import schemas


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Returns User by user id or None if not found"""
    query = select(models.User).where(models.User.id == user_id)
    return db.scalars(query).first()


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Returns User by username or None if not found"""
    query = select(models.User).where(models.User.username == username)
    return db.scalars(query).first()


def is_username_available(db: Session, username: str) -> bool:
    """Returns if username is available"""
    query = select(models.User.id).where(models.User.username == username)
    return db.scalar(query) is None


def patch_user_fullname(
    db: Session,
    user_id: int,
    user_patch: schemas.UserFullnameUpdate
) -> Optional[models.User]:
    user = get_user(db, user_id)

    if user is None:
        return None
    
    for key, value in user_patch.dict(exclude_unset=True).items():
        setattr(user, key, value)
    
    db.commit()
    return user
