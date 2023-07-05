from fastapi import APIRouter
from fastapi import Depends
from fastapi import responses
from fastapi import status

from market.apps.fastapi_app import deps
from market.apps.fastapi_app.routers.user import schemas
from market.modules.user.domain import models
from market.services import unit_of_work


router = APIRouter(
    prefix='/user',
    tags=['user'],
)


@router.get('/', response_model=schemas.UserRead)
def get_user(
    user: models.User = Depends(deps.get_user),
):
    """Returns information of the authorized user"""
    return schemas.UserRead.from_orm(user)


@router.put('/', response_model=schemas.UserRead)
def put_username(
    user_schema: schemas.UserDataUpdate,
    user: models.User = Depends(deps.get_user),
    uow: unit_of_work.UnitOfWork = Depends(deps.get_uow),
):
    """Allows to edit (PUT) the authorized user's information"""
    for key, value in user_schema.dict().items():
        setattr(user, key, value)

    updated_user = uow.users.update(user)
    
    uow.commit()
    
    return responses.RedirectResponse('/user', status.HTTP_303_SEE_OTHER)
