import dataclasses
from typing import Optional


@dataclasses.dataclass
class Image:
    image: str
    id: Optional[str] = None
