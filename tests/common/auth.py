import datetime
import json
import uuid
from typing import Any
from typing import Dict
from typing import Optional

import market.config
import market.modules.user.domain.models
import market.services.auth


class TokenAuth:
    token: str


    def __init__(self, token: str) -> None:
        self.token = token
    

    def __call__(self, r):
        r.headers['Authorization'] = f'Bearer {self.token}'
        return r


class LightAuthService(market.services.auth.AuthServiceImpl):
    def hash_password(self, password: str) -> str:
        return password + '_hash'


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

        return json.dumps(to_encode, default=str)
    

    def decode_token(self, token: str) -> Dict[str, Any]:
        return json.loads(token)
    

    def authenticate_user(
        self,
        username: str,
        password: str,
    ) -> Optional[market.modules.user.domain.models.User]:
        user = self.get_user_by_username(username)

        if user is None:
            return None
        
        if not self.verify_password(password, user.password):
            return None
        
        return user
    

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.hash_password(plain_password) == hashed_password


    def login(
        self,
        username: str,
        password: str,
    ) -> Optional[market.modules.user.domain.models.Token]:
        user = self.authenticate_user(username, password)
        if user is None:
            return None
        
        expire_minutes = market.config.get_access_token_expire_minutes()
        access_token_expires = datetime.timedelta(minutes=expire_minutes)
        access_token = self.create_access_token(
            data={'sub': user.username},
            expires_delta=access_token_expires
        )
        return market.modules.user.domain.models.Token(
            access_token=access_token,
            token_type='bearer',
        )
    

    def get_user(
        self,
        token: str,
    ) -> Optional[market.modules.user.domain.models.User]:
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
    ) -> market.modules.user.domain.models.User:
        hashed_password = self.hash_password(password)
        
        if not self.is_username_available(username):
            raise ValueError('Username is already taken')
        
        instance = market.modules.user.domain.models.User(
            id=user_id,
            username=username,
            password=hashed_password,
            full_name=full_name,
        )
        added_instance = self.repo.add(instance)

        return added_instance
