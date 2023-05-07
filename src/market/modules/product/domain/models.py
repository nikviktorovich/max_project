import dataclasses
from datetime import datetime
from typing import Optional


@dataclasses.dataclass
class Product:
    title: str
    stock: int
    price_rub: float
    owner_id: int
    id: Optional[int] = None
    description: str = ''
    added: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    is_active: bool = True