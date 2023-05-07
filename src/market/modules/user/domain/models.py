import dataclasses
from typing import Any


@dataclasses.dataclass
class User:
    username: str
    password: str
    id: Any = None
    full_name: str = ''


@dataclasses.dataclass
class Permission:
    name: str
    codename: str
    id: Any = None


@dataclasses.dataclass
class Group:
    name: str
    id: Any = None


@dataclasses.dataclass
class Token:
    access_token: str
    token_type: str
