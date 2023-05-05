import sqlalchemy
import sqlalchemy.orm


# TODO: Change url to environment variable value and change configuration
SQLALCHEMY_DATABASE_URL = 'sqlite:///./market_app.db'

engine = sqlalchemy.create_engine(
    url=SQLALCHEMY_DATABASE_URL,
    connect_args={'check_same_thread': False}
)

SessionLocal = sqlalchemy.orm.sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

Base = sqlalchemy.orm.declarative_base()