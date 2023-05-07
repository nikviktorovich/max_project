import dataclasses
from typing import Any


@dataclasses.dataclass
class CartItem:
    amount: int
    product_id: int
    user_id: int
    id: Any = None
