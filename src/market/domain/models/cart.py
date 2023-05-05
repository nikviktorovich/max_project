import dataclasses
from typing import Optional


@dataclasses.dataclass
class CartItem:
    amount: int
    product_id: int
    user_id: int
    id: Optional[int] = None
