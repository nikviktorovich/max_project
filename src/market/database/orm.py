import sqlalchemy
import sqlalchemy.orm

import market.config


DEFAULT_SESSION_FACTORY = sqlalchemy.orm.sessionmaker(
    bind=market.config.get_database_engine(),
)


Base = sqlalchemy.orm.declarative_base()
