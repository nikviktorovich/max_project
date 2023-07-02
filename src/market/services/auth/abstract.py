import uuid
from typing import Optional

from market.modules.user.domain import models


class AuthService:
    def get_user_by_username(self, username: str) -> Optional[models.User]:
        ...
    

    def is_username_available(self, username: str) -> bool:
        ...
    

    def authenticate_user(
        self,
        username: str,
        password: str,
    ) -> Optional[models.User]:
        ...
    

    def login(self, username: str, password: str) -> Optional[models.Token]:
        ...
    

    def register_user(
        self,
        user_id: uuid.UUID,
        username: str,
        password: str,
        full_name: str = '',
    ) -> models.User:
        ...
