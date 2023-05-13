import os

import sqlalchemy
import sqlalchemy.orm


def get_hash_algorithm() -> str:
    return os.environ['HASH_ALGORITHM']


def get_hash_secret_key() -> str:
    return os.environ['HASH_SECRET_KEY']


def get_access_token_expire_minutes() -> int:
    return int(os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'])


def get_database_connection_url() -> str:
    return os.environ['DATABASE_CONNECTION_URL']


def get_database_engine() -> sqlalchemy.Engine:
    connection_url = get_database_connection_url()
    connect_args = {}

    if connection_url.startswith('sqlite'):
        connect_args['check_same_thread'] = False

    engine = sqlalchemy.create_engine(
        url=connection_url,
        connect_args=connect_args,
    )

    return engine
