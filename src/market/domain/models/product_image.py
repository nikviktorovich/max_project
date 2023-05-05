import dataclasses
from typing import Optional


@dataclasses.dataclass
class ProductImage:
    product_id: int
    image_id: int
    id: Optional[int] = None