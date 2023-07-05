import fastapi.testclient
import pytest

from market.apps.fastapi_app import deps
from market.apps.fastapi_app import fastapi_main

from . import common


@pytest.fixture(scope='module')
def app():
    yield fastapi_main.app
    fastapi_main.app.dependency_overrides.clear()


@pytest.fixture(scope='module')
def lw_app():
    factory = lambda repo: common.LightAuthService(repo)
    get_factory = lambda: factory
    fastapi_main.app.dependency_overrides[deps.get_auth_service_factory] = get_factory
    yield fastapi_main.app
    fastapi_main.app.dependency_overrides.clear()


@pytest.fixture(scope='module')
def client(app):
    return fastapi.testclient.TestClient(app)
