import fastapi.testclient
import pytest

from market.apps.fastapi_app import fastapi_main


@pytest.fixture(scope='module')
def app():
    yield fastapi_main.app
    fastapi_main.app.dependency_overrides.clear()


@pytest.fixture(scope='module')
def client(app):
    return fastapi.testclient.TestClient(app)
