import dataclasses
import uuid
from datetime import datetime
from typing import Optional


@dataclasses.dataclass
class Product:
    id: uuid.UUID
    title: str
    stock: int
    price_rub: float
    owner_id: uuid.UUID
    description: str = ''
    added: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    is_active: bool = True