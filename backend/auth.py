import datetime
import logging
import passlib.context
from typing import Any, Dict, Optional
from jose import jwt
from sqlalchemy.orm import Session
from database import SessionLocal
from database import crud
from database import models
from database import schemas


logger = logging.getLogger(__name__)


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "c709df8055abd0301269d0c9da919adb7da70507d68271d7487170d825469744"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


_pwd_context = passlib.context.CryptContext(schemes=['bcrypt'], deprecated='auto')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def authenticate_user(db: Session,
                      username: str,
                      password: str
                      ) -> Optional[models.User]:
    user = crud.get_user_by_username(db, username)
    
    if user is None:
        return None
    
    if not verify_password(password, user.password):
        return None
    
    return user


def create_access_token(data: dict,
                        expires_delta: Optional[datetime.timedelta] = None,
                        ) -> str:
    if expires_delta is None:
        expires_delta = datetime.timedelta(minutes=15)
    
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + expires_delta
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """Decodes JWT token
    
    Raises:
        jose.JWTError:
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def login(db: Session, username: str, password: str) -> Optional[schemas.Token]:
    user = authenticate_user(db, username, password)
    if user is None:
        return None
    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.username},
        expires_delta=access_token_expires
    )
    return schemas.Token(access_token=access_token, token_type='bearer')


def register_user(db: Session, user: schemas.UserCreate) -> schemas.Token:
    hashed_password = hash_password(user.password)
    
    if not crud.is_username_available(db, user.username):
        raise ValueError('Username is already taken')
    
    user_db = models.User(
        username=user.username,
        password=hashed_password,
        full_name=user.full_name,
    )
    db.add(user_db)
    db.commit()
    
    token = login(db, user.username, user.password)
    
    if token is None:
        logger.error(f'User "{user.username}" has been registered but not logged in')
        raise ValueError('Error registering a user. Please, try later.')
    
    return token
