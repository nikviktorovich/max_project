from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from market.apps.fastapi_app import deps
from market.modules.user import repositories
from market.modules.user import schemas
from market.modules.user import unit_of_work
from market.modules.user.domain import models


router = APIRouter(
    prefix='/user',
    tags=['user'],
)


@router.get('/', response_model=schemas.UserRead)
def get_user(
    user: models.User = Depends(deps.get_user)
):
    """Returns information of the authorized user"""
    return user


@router.patch('/', response_model=schemas.UserRead)
def patch_username(
    user_schema: schemas.UserDataUpdate,
    user: models.User = Depends(deps.get_user),
):
    """Allows to edit (PATCH) the authorized user's information"""
    with unit_of_work.UserUnitOfWork() as uow:
        for key, value in user_schema.dict(exclude_unset=True).items():
            setattr(user, key, value)

        patched_user = uow.users.add(user)

        uow.commit()
        
        return schemas.UserRead.from_orm(patched_user)


@router.put('/', response_model=schemas.UserRead)
def put_username(
    user_schema: schemas.UserDataPut,
    user: models.User = Depends(deps.get_user),
):
    """Allows to edit (PUT) the authorized user's information"""
    with unit_of_work.UserUnitOfWork() as uow:
        for key, value in user_schema.dict().items():
            setattr(user, key, value)

        updated_user = uow.users.add(user)
        
        uow.commit()
        
        return schemas.UserRead.from_orm(updated_user)