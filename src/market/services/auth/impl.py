import datetime
import logging
import uuid
from typing import Any
from typing import Dict
from typing import Optional

import passlib.context
from jose import jwt

import market.config
from market.modules.user.domain import models
from market.modules.user import repositories

from market.services.auth import abstract


logger = logging.getLogger(__name__)


class AuthServiceImpl(abstract.AuthService):
    pwd_context: passlib.context.CryptContext
    repo: repositories.UserRepository


    def __init__(self, repo: repositories.UserRepository) -> None:
        self.pwd_context = passlib.context.CryptContext(
            schemes=['bcrypt'],
            deprecated='auto',
        )
        self.repo = repo


    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)


    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)


    def get_user_by_username(self, username: str) -> Optional[models.User]:
        matching_users_list = self.repo.list(username=username)
        
        if not matching_users_list:
            return None
        
        [user] = matching_users_list

        return user


    def is_username_available(self, username: str) -> bool:
        user = self.get_user_by_username(username)
        return user is None


    def authenticate_user(
        self,
        username: str,
        password: str,
    ) -> Optional[models.User]:
        user = self.get_user_by_username(username)

        if user is None:
            return None
        
        if not self.verify_password(password, user.password):
            return None
        
        return user


    def create_access_token(
        self,
        data: dict,
        expires_delta: Optional[datetime.timedelta] = None,
    ) -> str:
        if expires_delta is None:
            expires_delta = datetime.timedelta(minutes=15)
        
        to_encode = data.copy()
        expire = datetime.datetime.utcnow() + expires_delta
        to_encode.update({'exp': expire})

        secret_key = market.config.get_hash_secret_key()
        algorithm = market.config.get_hash_algorithm()
        encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)

        return encoded_jwt


    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decodes JWT token
        
        Raises:
            jose.JWTError:
        """
        secret_key = market.config.get_hash_secret_key()
        algorithm = market.config.get_hash_algorithm()
        return jwt.decode(token, secret_key, algorithms=[algorithm])


    def login(self, username: str, password: str) -> Optional[models.Token]:
        user = self.authenticate_user(username, password)
        if user is None:
            return None
        
        expire_minutes = market.config.get_access_token_expire_minutes()
        access_token_expires = datetime.timedelta(minutes=expire_minutes)
        access_token = self.create_access_token(
            data={'sub': user.username},
            expires_delta=access_token_expires
        )
        return models.Token(access_token=access_token, token_type='bearer')


    def get_user(
        self,
        token: str,
    ) -> Optional[models.User]:
        """Reads the token and returns the corresponding user
        Reads the token and returns the corresponding user. If user is not active
        or token is expired (not implemented for simplicity) None is returned.
        """
        decoded_data = self.decode_token(token)
        username = decoded_data['sub']
        user = self.get_user_by_username(username)
        return user


    def register_user(
        self,
        user_id: uuid.UUID,
        username: str,
        password: str,
        full_name: str = '',
    ) -> models.User:
        hashed_password = self.hash_password(password)
        
        if not self.is_username_available(username):
            raise ValueError('Username is already taken')
        
        instance = models.User(
            id=user_id,
            username=username,
            password=hashed_password,
            full_name=full_name,
        )
        added_instance = self.repo.add(instance)

        return added_instance
