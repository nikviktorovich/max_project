import dataclasses
from typing import Any


@dataclasses.dataclass
class Image:
    image: str
    id: Any = None
