import unittest
import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm
import database
import main
from fastapi.testclient import TestClient


SQLALCHEMY_DATABASE_URL = 'sqlite:///./test_market_app.db'

engine = sqlalchemy.create_engine(
    url=SQLALCHEMY_DATABASE_URL,
    connect_args={'check_same_thread': False}
)

TestingSessionLocal = sqlalchemy.orm.sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

database.Base.metadata.create_all(bind=engine)


def get_test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


main.app.dependency_overrides[main.get_db] = get_test_db

client = TestClient(main.app)


class TestSelect(unittest.TestCase):
    pass
