from datetime import datetime
from typing import Optional

import pydantic


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
    owner_id: int


class ProductPut(ProductCreate):
    pass


class Product(ProductBase):
    id: Optional[int] = None
    added: datetime
    last_updated: datetime
    owner_id: int

    class Config:
        orm_mode = True
