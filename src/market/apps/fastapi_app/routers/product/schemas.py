import uuid
from datetime import datetime

import pydantic


class ProductBase(pydantic.BaseModel):
    title: str = pydantic.Field(min_length=8, max_length=255)
    description: str = ''
    stock: int
    price_rub: float
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductRead(ProductBase):
    id: uuid.UUID
    added: datetime
    last_updated: datetime
    owner_id: uuid.UUID

    class Config:
        orm_mode = True


class ProductPut(ProductCreate):
    pass
