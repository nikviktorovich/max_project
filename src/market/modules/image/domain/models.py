import dataclasses
import uuid


@dataclasses.dataclass
class Image:
    id: uuid.UUID
    image: str
