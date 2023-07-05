import os
import shutil
import uuid

import fastapi
import pytest
from fastapi import status
from fastapi import testclient

import market.modules.image.domain.models
import market.services.auth
from market.apps.fastapi_app import deps

from .. import common


@pytest.mark.usefixtures('app', 'client')
def test_image_endpoint_upload_image_success(
    app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    image_repo = common.FakeImageRepository([])
    uow = common.FakeUnitOfWork(images=image_repo)
    app.dependency_overrides[deps.get_uow] = lambda: uow

    temp_path = './tests/content/temp'
    app.dependency_overrides[deps.get_media_path] = lambda: temp_path
    os.makedirs(temp_path)
    assert len(os.listdir(temp_path)) == 0

    with open('./tests/content/test_image.png', 'rb') as f:
        response = client.post('/images', files={'image': f})
    
    assert response.status_code == status.HTTP_200_OK
    assert len(os.listdir(temp_path)) == 1

    shutil.rmtree(temp_path)


def test_image_endpoint_get_existing_image_record(
    app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    image = market.modules.image.domain.models.Image(
        id=uuid.uuid4(),
        image='filename.png',
    )
    image_repo = common.FakeImageRepository([image])
    uow = common.FakeUnitOfWork(images=image_repo)
    app.dependency_overrides[deps.get_uow] = lambda: uow

    response = client.get(f'/images/{image.id}')
    assert response.status_code == status.HTTP_200_OK


def test_image_endpoint_get_nonexisting_image_record(
    app: fastapi.FastAPI,
    client: testclient.TestClient,
):
    image_repo = common.FakeImageRepository([])
    uow = common.FakeUnitOfWork(images=image_repo)
    app.dependency_overrides[deps.get_uow] = lambda: uow

    response = client.get(f'/images/{uuid.uuid4()}')
    assert response.status_code == status.HTTP_404_NOT_FOUND
