from fastapi import APIRouter
from fastapi import Depends

from market.apps.fastapi_app import deps
from market.modules.user import schemas
from market.modules.user.domain import models
from market.services import unit_of_work


router = APIRouter(
    prefix='/user',
    tags=['user'],
)


@router.get('/', response_model=schemas.UserRead)
def get_user(
    user: models.User = Depends(deps.get_user)
):
    """Returns information of the authorized user"""
    return schemas.UserRead.from_orm(user)


@router.patch('/', response_model=schemas.UserRead)
def patch_username(
    user_schema: schemas.UserDataUpdate,
    user: models.User = Depends(deps.get_user),
    uow: unit_of_work.UnitOfWork = Depends(deps.get_uow),
):
    """Allows to edit (PATCH) the authorized user's information"""
    for key, value in user_schema.dict(exclude_unset=True).items():
        setattr(user, key, value)

    patched_user = uow.users.add(user)

    uow.commit()
    
    return schemas.UserRead.from_orm(patched_user)


@router.put('/', response_model=schemas.UserRead)
def put_username(
    user_schema: schemas.UserDataPut,
    user: models.User = Depends(deps.get_user),
    uow: unit_of_work.UnitOfWork = Depends(deps.get_uow),
):
    """Allows to edit (PUT) the authorized user's information"""
    for key, value in user_schema.dict().items():
        setattr(user, key, value)

    updated_user = uow.users.add(user)
    
    uow.commit()
    
    return schemas.UserRead.from_orm(updated_user)