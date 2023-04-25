import pydantic
from datetime import datetime
from typing import Optional
from . import User
from . import UserRead


class ProductBase(pydantic.BaseModel):
    title: str
    description: str = ''
    stock: int
    price_rub: float
    is_active: bool = True


class ProductCreate(ProductBase):
    @pydantic.validator('title')
    def title_valid_length(cls, v):
        if len(v) < 8:
            raise ValueError('Title must be at least 8 characters long')
        
        if len(v) > 255:
            raise ValueError('Title is too long')
        
        return v


class ProductRead(ProductBase):
    id: int
    added: datetime
    last_updated: datetime
    owner: UserRead
    
    class Config:
        orm_mode=True


class ProductUpdate(pydantic.BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    stock: Optional[int] = None
    price_rub: Optional[float] = None
    is_active: Optional[bool] = None

    @pydantic.validator('title')
    def title_valid_length(cls, v):
        if len(v) < 8:
            raise ValueError('Title must be at least 8 characters long')
        
        if len(v) > 255:
            raise ValueError('Title is too long')
        
        return v


class ProductPut(ProductCreate):
    pass


class Product(ProductBase):
    id: int
    added: datetime
    last_updated: datetime
    owner: User
    
    class Config:
        orm_mode = True
