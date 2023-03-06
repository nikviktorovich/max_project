import pydantic


class CartItemBase(pydantic.BaseModel):
    product_id: int
    amount: int

    @pydantic.validator('amount')
    def valid_amount(cls, v: int):
        if v <= 0:
            raise ValueError('Invalid amount')
        return v

    class Config:
        orm_mode = True


class CartItemCreate(CartItemBase):
    pass


class CartItemCreateInternal(CartItemCreate):
    user_id: int


class CartItemRead(CartItemBase):
    pass


class CartItemUpdate(pydantic.BaseModel):
    amount: int

    @pydantic.validator('amount')
    def valid_amount(cls, v: int):
        if v <= 0:
            raise ValueError('Invalid amount')
        return v


class CartItemUpdateInternal(CartItemUpdate):
    user_id: int
    product_id: int


class CartItemDelete(pydantic.BaseModel):
    user_id: int
    product_id: int
