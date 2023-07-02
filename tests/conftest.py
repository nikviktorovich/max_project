import datetime
import uuid
from typing import Any
from typing import Dict
from typing import List
import fastapi.testclient
import pytest

from market.apps.fastapi_app import fastapi_main


@pytest.fixture(scope='session')
def app():
    return fastapi_main.app


@pytest.fixture(scope='session')
def client(app):
    return fastapi.testclient.TestClient(app)
