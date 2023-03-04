import pydantic
from datetime import datetime
from typing import List, Optional
from . import Image
from . import ImageRead
from . import User
from . import UserRead


class ProductImageBase(pydantic.BaseModel):
    pass


class ProductImageCreate(ProductImageBase):
    image_id: int

    class Config:
        orm_mode = True


class ProductImageRead(ProductImageBase):
    id: int
    product_id: int
    image: 'ImageRead'
    
    class Config:
        orm_mode=True


class ProductImage(ProductImageRead):
    class Config:
        orm_mode = True


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
    images: List['ProductImageRead']
    
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


class Product(ProductBase):
    id: int
    added: datetime
    last_updated: datetime
    owner: User
    images: List['ProductImage']
    
    class Config:
        orm_mode = True
