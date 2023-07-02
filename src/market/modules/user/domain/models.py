import dataclasses
import uuid


@dataclasses.dataclass
class User:
    id: uuid.UUID
    username: str
    password: str
    full_name: str = ''


@dataclasses.dataclass
class Permission:
    id: uuid.UUID
    name: str
    codename: str


@dataclasses.dataclass
class Group:
    id: uuid.UUID
    name: str


@dataclasses.dataclass
class Token:
    access_token: str
    token_type: str
