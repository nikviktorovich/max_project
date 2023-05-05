import sqlalchemy
import sqlalchemy.orm

from .. import config


engine = sqlalchemy.create_engine(
    url=config.get_database_connection_url(),
    connect_args={'check_same_thread': False}
)

SessionLocal = sqlalchemy.orm.sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

Base = sqlalchemy.orm.declarative_base()