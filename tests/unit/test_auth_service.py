import uuid

from market import services

from .. import common


def test_auth_service_successful_register():
    user_repo = common.FakeUserRepository([])
    service = services.AuthService(user_repo) # type: ignore

    user_id = uuid.uuid4()
    service.register_user(user_id, 'username', 'password')
    assert user_repo.get(user_id).username == 'username'


def test_auth_service_is_username_available():
    user_repo = common.FakeUserRepository([])
    service = services.AuthService(user_repo) # type: ignore
    service.register_user(uuid.uuid4(), 'username', 'password')

    assert service.is_username_available('username') == False
    assert service.is_username_available('non_existing_username') == True
