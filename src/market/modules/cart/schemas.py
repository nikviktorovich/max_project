import uuid

import pydantic


class CartItemBase(pydantic.BaseModel):
    product_id: uuid.UUID
    amount: int

    @pydantic.validator('amount')
    def valid_amount(cls, v: int):
        if v <= 0:
            raise ValueError('Invalid amount')
        return v


class CartItemCreate(CartItemBase):
    pass


class CartItemRead(CartItemBase):
    id: uuid.UUID

    class Config:
        orm_mode = True


class CartItemUpdate(CartItemBase):
    pass


class CartItem(CartItemBase):
    id: uuid.UUID
    user_id: uuid.UUID