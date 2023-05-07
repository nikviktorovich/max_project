import pydantic
from typing import Optional


class CartItemBase(pydantic.BaseModel):
    product_id: int
    amount: int

    @pydantic.validator('amount')
    def valid_amount(cls, v: int):
        if v <= 0:
            raise ValueError('Invalid amount')
        return v


class CartItemCreate(CartItemBase):
    pass


class CartItemRead(CartItemBase):
    id: int


class CartItemUpdate(CartItemBase):
    pass


class CartItem(CartItemBase):
    id: Optional[int] = None
    user_id: int

    class Config:
        orm_mode = True