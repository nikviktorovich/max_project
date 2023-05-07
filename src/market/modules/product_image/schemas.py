import pydantic
from typing import Optional


class ProductImageBase(pydantic.BaseModel):
    product_id: int
    image_id: int


class ProductImageCreate(ProductImageBase):
    pass


class ProductImageRead(ProductImageBase):
    id: int


class ProductImage(ProductImageBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True