import logging
import uuid
from typing import List

from sqlalchemy.orm import Session

import market.common.errors
from market.modules.user.domain import models


logger = logging.getLogger(__name__)


class UserRepository:
    """SQLAlchemy repository of user data"""
    session: Session


    def __init__(self, session: Session) -> None:
        self.session = session
    

    def get(self, user_id: uuid.UUID) -> models.User:
        queryset = self.session.query(models.User)
        queryset = queryset.filter_by(id=user_id)
        instance = queryset.first()

        if instance is None:
            raise market.common.errors.NotFoundError(
                f'Unable to find a user with id={user_id}',
            )

        return instance
    

    def add(self, user: models.User) -> models.User:
        self.session.add(user)
        return user
    

    def list(self, **filters) -> List[models.User]:
        user_set = self.session.query(models.User)

        if filters:
            user_set = user_set.filter_by(**filters)
        
        return user_set.all()
    

    def delete(self, user: models.User) -> None:
        self.session.delete(user)
    

    def update(self, user: models.User, **fields) -> models.User:
        for attribute, value in fields.items():
            setattr(user, attribute, value)
        
        return user
