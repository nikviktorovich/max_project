import uuid

import pydantic


class ProductImageBase(pydantic.BaseModel):
    product_id: uuid.UUID
    image_id: uuid.UUID


class ProductImageCreate(ProductImageBase):
    pass


class ProductImageRead(ProductImageBase):
    id: uuid.UUID

    class Config:
        orm_mode = True


class ProductImage(ProductImageBase):
    id: uuid.UUID