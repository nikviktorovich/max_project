import dataclasses
from typing import Optional


@dataclasses.dataclass
class User:
    username: str
    password: str
    id: Optional[int] = None
    full_name: str = ''


@dataclasses.dataclass
class Permission:
    name: str
    codename: str
    id: Optional[int] = None


@dataclasses.dataclass
class Group:
    name: str
    id: Optional[int] = None


@dataclasses.dataclass
class Token:
    access_token: str
    token_type: str
