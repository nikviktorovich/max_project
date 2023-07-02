from typing import Callable

import sqlalchemy.orm

import market.modules.cart.repositories
import market.modules.image.repositories
import market.modules.product.repositories
import market.modules.product_image.repositories
import market.modules.user.repositories

from market.services.unit_of_work import abstract


class SQLAlchemyUnitOfWork(abstract.UnitOfWork):
    """Unit Of Work wrapper over SQLAlchemy"""
    session_factory: Callable[[], sqlalchemy.orm.Session]
    session: sqlalchemy.orm.Session


    def __init__(
        self,
        session_factory: Callable[[], sqlalchemy.orm.Session],
    ) -> None:
        self.session_factory = session_factory


    def __enter__(self) -> abstract.UnitOfWork:
        self.session = self.session_factory()
        self.cart = market.modules.cart.repositories.CartRepository(
            self.session,
        )
        self.images = market.modules.image.repositories.ImageRepository(
            self.session,
        )
        self.products = market.modules.product.repositories.ProductRepository(
            self.session,
        )
        self.product_images = market.modules.product_image.\
            repositories.ProductImageRepository(self.session)
        self.users = market.modules.user.repositories.UserRepository(
            self.session,
        )
        return self
    

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
    

    def commit(self) -> None:
        self.session.commit()
    

    def rollback(self) -> None:
        self.session.rollback()
