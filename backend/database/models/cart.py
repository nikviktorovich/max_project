from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from .auth import User
from .product import Product
from .. import Base


class CartItem(Base):
    __tablename__ = 'cartitems'
    __table_args__ = (UniqueConstraint('product_id', 'user_id'), )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    amount: Mapped[int] = mapped_column()
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    product: Mapped[Product] = relationship(Product)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped[User] = relationship(User)
