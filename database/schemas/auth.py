import pydantic
from typing import Optional


class Token(pydantic.BaseModel):
    access_token: str
    token_type: str


class UserBase(pydantic.BaseModel):
    username: str
    full_name: str = ''
    
    @pydantic.validator('username')
    def username_valid_length(cls, v):
        if len(v) < 8:
            raise ValueError('Username must be at least 8 characters long')
        if len(v) > 150:
            raise ValueError('Username is too long')
        return v


class UserCreate(UserBase):
    password: str
    
    @pydantic.validator('password')
    def password_valid_length(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if len(v) > 255:
            raise ValueError('Password is too long')
        return v


class UserRead(UserBase):
    pass

    class Config:
        orm_mode=True


class User(UserCreate):
    id: int


class UserFullnameUpdate(pydantic.BaseModel):
    full_name: Optional[str] = None


class UserFullnamePut(pydantic.BaseModel):
    full_name: str = ''