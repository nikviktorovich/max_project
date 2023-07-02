import dataclasses
import uuid


@dataclasses.dataclass
class ProductImage:
    id: uuid.UUID
    product_id: uuid.UUID
    image_id: uuid.UUID
