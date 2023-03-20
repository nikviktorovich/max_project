from typing import List, Optional
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from .. import Base


# Many-to-many relationship of groups assigned to individual users
user_groups = Table(
    'user_groups',
    Base.metadata,
    Column('user_id', ForeignKey('users.id')),
    Column('group_id', ForeignKey('groups.id')),
)

# Many-to-many relationship of permissions assigned to individual users
user_permissions = Table(
    'user_permissions',
    Base.metadata,
    Column('user_id', ForeignKey('users.id')),
    Column('permission_id', ForeignKey('permissions.id')),
)

# Many-to-many relationship of permissions assigned to groups
group_permissions = Table(
    'group_permissions',
    Base.metadata,
    Column('group_id', ForeignKey('groups.id')),
    Column('permission_id', ForeignKey('permissions.id')),
)


class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(150), unique=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    password: Mapped[str] = mapped_column(String(255))
    groups: Mapped[List['Group']] = relationship(secondary=user_groups)
    permissions: Mapped[List['Permission']] = relationship(secondary=user_permissions)


class Permission(Base):
    __tablename__ = 'permissions'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    codename: Mapped[str] = mapped_column(String(100))


class Group(Base):
    __tablename__ = 'groups'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    permissions: Mapped[List['Permission']] = relationship(secondary=group_permissions)
