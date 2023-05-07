import sqlalchemy
import sqlalchemy.orm

import market.config


engine = sqlalchemy.create_engine(
    url=market.config.get_database_connection_url(),
    connect_args={'check_same_thread': False}
)

SessionLocal = sqlalchemy.orm.sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

Base = sqlalchemy.orm.declarative_base()
