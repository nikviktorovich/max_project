import pydantic
from .media import ImageRead


class ProductImageBase(pydantic.BaseModel):
    pass


class ProductImageCreate(ProductImageBase):
    product_id: int
    image_id: int

    class Config:
        orm_mode = True


class ProductImageRead(ProductImageBase):
    product_id: int
    image: 'ImageRead'
    
    class Config:
        orm_mode=True


class ProductImage(ProductImageRead):
    class Config:
        orm_mode = True