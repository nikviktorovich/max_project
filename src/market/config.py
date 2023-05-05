import os


def get_hash_algorithm() -> str:
    return os.environ['HASH_ALGORITHM']


def get_hash_secret_key() -> str:
    return os.environ['HASH_SECRET_KEY']


def get_access_token_expire_minutes() -> int:
    return int(os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'])


def get_database_connection_url() -> str:
    return os.environ['DATABASE_CONNECTION_URL']
