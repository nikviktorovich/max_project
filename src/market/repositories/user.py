import logging
from typing import List

from sqlalchemy.orm import Session

from . import exceptions
from .. import domain


logger = logging.getLogger(__name__)


class UserRepository:
    """SQLAlchemy repository of user data"""
    session: Session


    def __init__(self, session: Session) -> None:
        self.session = session
    

    def get(self, user_id: int) -> domain.models.User:
        queryset = self.session.query(domain.models.User)
        queryset = queryset.filter_by(id=user_id)
        instance = queryset.first()

        if instance is None:
            raise exceptions.NotFoundError(
                f'Unable to find a user with id={user_id}',
            )

        return instance
    

    def add(self, user: domain.models.User) -> domain.models.User:
        self.session.add(user)
        return user
    

    def list(self, **filters) -> List[domain.models.User]:
        user_set = self.session.query(domain.models.User)

        if filters:
            user_set = user_set.filter_by(**filters)
        
        return user_set.all()
    

    def delete(self, user: domain.models.User) -> None:
        self.session.delete(user)
