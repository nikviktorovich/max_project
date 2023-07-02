import uuid
from datetime import datetime
from typing import List

from sqlalchemy import func
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped

import market.database.orm
from market.database.models.auth import User
from market.database.models.media import Image


class ProductImage(market.database.orm.Base):
    
    __tablename__ = 'productimages'
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('products.id'))
    product: Mapped['Product'] = relationship(back_populates='images')
    image_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('images.id'), unique=True)
    image: Mapped['Image'] = relationship()


class Product(market.database.orm.Base):
    __tablename__ = 'products'
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str]
    stock: Mapped[int]
    price_rub: Mapped[float]
    is_active: Mapped[bool] = mapped_column(default=True)
    added: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now()
    )
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now()
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id'))
    owner: Mapped['User'] = relationship()
    images: Mapped[List['ProductImage']] = relationship(
        back_populates='product',
        cascade="all, delete-orphan"
    )
