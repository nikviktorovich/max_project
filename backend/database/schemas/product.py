import pydantic
from datetime import datetime
from typing import List
from . import Image
from . import User
from . import UserRead


class ProductImageBase(pydantic.BaseModel):
    pass


class ProductImageCreate(ProductImageBase):
    image_id: int


class ProductImage(ProductImageBase):
    id: int
    image: 'Image'
    
    class Config:
        orm_mode=True


class ProductImageRead(ProductImage):
    pass


class ProductBase(pydantic.BaseModel):
    title: str
    description: str
    stock: int
    price_rub: float
    is_active: bool


class ProductCreate(ProductBase):
    images: List[int]
    
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
    images: List['ProductImage']
    
    class Config:
        orm_mode=True


class Product(ProductBase):
    id: int
    added: datetime
    last_updated: datetime
    owner: User
    images: List['ProductImage']
    
    class Config:
        orm_mode = True
