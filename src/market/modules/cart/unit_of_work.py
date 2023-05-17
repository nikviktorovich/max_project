import sqlalchemy.orm

import market.config
import market.database.orm
from market.modules.cart import repositories


class CartUnitOfWork:
    session_factory: sqlalchemy.orm.sessionmaker
    session: sqlalchemy.orm.Session
    cart_items: repositories.CartRepository


    def __init__(
        self,
        session_factory=market.database.orm.DEFAULT_SESSION_FACTORY,
    ) -> None:
        self.session_factory = session_factory


    def __enter__(self):
        self.session = self.session_factory()
        self.cart_items = repositories.CartRepository(self.session)
        return self
    

    def __exit__(self, *args, **kwargs):
        self.session.close()
    

    def commit(self):
        self.session.commit()
    

    def rollback(self):
        self.session.rollback()
