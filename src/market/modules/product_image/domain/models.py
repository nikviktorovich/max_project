import dataclasses
from typing import Any


@dataclasses.dataclass
class ProductImage:
    product_id: int
    image_id: int
    id: Any = None
