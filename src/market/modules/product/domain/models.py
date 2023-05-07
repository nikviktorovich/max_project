import dataclasses
from datetime import datetime
from typing import Any
from typing import Optional


@dataclasses.dataclass
class Product:
    title: str
    stock: int
    price_rub: float
    owner_id: int
    id: Any = None
    description: str = ''
    added: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    is_active: bool = True