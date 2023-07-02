import dataclasses
import uuid


@dataclasses.dataclass
class CartItem:
    id: uuid.UUID
    amount: int
    product_id: uuid.UUID
    user_id: uuid.UUID
