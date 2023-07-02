import uuid

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

import market.database.orm


class Image(market.database.orm.Base):
    __tablename__ = 'images'
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    image: Mapped[str]
