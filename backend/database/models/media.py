from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from .. import Base


class Image(Base):
    __tablename__ = 'images'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    media_path: Mapped[str]
