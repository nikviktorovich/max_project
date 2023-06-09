import uuid

from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

import market.database.orm
from market.database.models.auth import User
from market.database.models.product import Product


class CartItem(market.database.orm.Base):
    __tablename__ = 'cartitems'
    __table_args__ = (
        UniqueConstraint(
            'product_id',
            'user_id',
            name='user_product_unique_constraint',
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, index=True)
    amount: Mapped[int] = mapped_column()
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('products.id'))
    product: Mapped[Product] = relationship(Product)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id'))
    user: Mapped[User] = relationship(User)
