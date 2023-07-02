import uuid

import pytest

import market.services.auth
from market.modules.user.domain import models

from .. import common


def test_auth_service_get_user_by_username():
    user_repo = common.FakeUserRepository([
        models.User(
            id=uuid.uuid4(),
            username='username',
            password='password_hash',
        ),
    ])
    service = market.services.auth.AuthServiceImpl(user_repo) # type: ignore

    assert service.get_user_by_username('username') is not None
    assert service.get_user_by_username('non_existing_username') is None


def test_auth_service_is_username_available():
    user_repo = common.FakeUserRepository([])
    service = market.services.auth.AuthServiceImpl(user_repo) # type: ignore
    service.register_user(uuid.uuid4(), 'username', 'password')

    assert service.is_username_available('username') == False
    assert service.is_username_available('non_existing_username') == True


def test_auth_service_authenticate_user():
    user_repo = common.FakeUserRepository([])
    service = market.services.auth.AuthServiceImpl(user_repo) # type: ignore
    service.register_user(uuid.uuid4(), 'username', 'password')

    assert service.authenticate_user('username', 'password') is not None
    assert service.authenticate_user('username', 'invalid_password') is None


def test_auth_service_login():
    user_repo = common.FakeUserRepository([])
    service = market.services.auth.AuthServiceImpl(user_repo) # type: ignore
    service.register_user(uuid.uuid4(), 'username', 'password')

    assert service.login('username', 'password') is not None
    assert service.login('username', 'invalid_password') is None
    assert service.login('non_existing_username', 'does_not_matter') is None


def test_auth_service_register():
    user_repo = common.FakeUserRepository([])
    service = market.services.auth.AuthServiceImpl(user_repo) # type: ignore

    user_id = uuid.uuid4()
    service.register_user(user_id, 'username', 'password')
    assert user_repo.get(user_id).username == 'username'

    with pytest.raises(ValueError):
        service.register_user(uuid.uuid4(), 'username', 'does_not_matter')
