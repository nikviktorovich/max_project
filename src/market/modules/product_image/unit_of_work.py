import sqlalchemy.orm

import market.config
import market.database.orm
import market.modules.image.repositories
import market.modules.product.repositories
from market.modules.product_image import repositories


class ProductImageUnitOfWork:
    session_factory: sqlalchemy.orm.sessionmaker
    session: sqlalchemy.orm.Session
    product_images: repositories.ProductImageRepository
    products: market.modules.product.repositories.ProductRepository
    images: market.modules.image.repositories.ImageRepository


    def __init__(
        self,
        session_factory=market.database.orm.DEFAULT_SESSION_FACTORY,
    ) -> None:
        self.session_factory = session_factory


    def __enter__(self):
        self.session = self.session_factory()
        self.product_images = repositories.ProductImageRepository(self.session)
        self.products = market.modules.product.repositories.ProductRepository(
            self.session,
        )
        self.images = market.modules.image.repositories.ImageRepository(
            self.session,
        )
        return self
    

    def __exit__(self, *args, **kwargs):
        self.session.close()
    

    def commit(self):
        self.session.commit()
    

    def rollback(self):
        self.session.rollback()
