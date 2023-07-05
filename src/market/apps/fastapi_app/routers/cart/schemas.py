import uuid

import pydantic


class CartItemBase(pydantic.BaseModel):
    product_id: uuid.UUID
    amount: int = pydantic.Field(gt=0)


class CartItemCreate(CartItemBase):
    pass


class CartItemRead(CartItemBase):
    id: uuid.UUID

    class Config:
        orm_mode = True


class CartItemUpdate(CartItemCreate):
    pass
