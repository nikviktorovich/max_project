import uuid

import pydantic


class Token(pydantic.BaseModel):
    access_token: str
    token_type: str

    class Config:
        orm_mode=True


class UserBase(pydantic.BaseModel):
    username: str = pydantic.Field(min_length=8, max_length=150)
    full_name: str = ''


class UserCreate(UserBase):
    password: str = pydantic.Field(min_length=8, max_length=255)


class UserRead(UserBase):
    id: uuid.UUID

    class Config:
        orm_mode=True
