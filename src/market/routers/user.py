from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session
from .. import crud
from .. import deps
from .. import models
from .. import schemas


router = APIRouter(
    prefix='/user',
    tags=['user'],
)


@router.get('/', response_model=schemas.UserRead)
def get_user(user: models.User = Depends(deps.get_user)):
    """Returns information of the authorized user"""
    return user


@router.patch('/', response_model=schemas.UserRead)
def patch_username(
    user_patch: schemas.UserFullnameUpdate,
    user: models.User = Depends(deps.get_user),
    db: Session = Depends(deps.get_db)
):
    """Allows to edit (PATCH) the authorized user's information"""
    patched_user = crud.patch_user_fullname(db, user.id, user_patch)

    if patched_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You need to authorize first',
        )
    
    return patched_user


@router.put('/', response_model=schemas.UserRead)
def put_username(
    user_put: schemas.UserFullnamePut,
    user: models.User = Depends(deps.get_user),
    db: Session = Depends(deps.get_db)
):
    """Allows to edit (PUT) the authorized user's information"""
    updated_user = crud.put_user_fullname(db, user.id, user_put)

    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You need to authorize first',
        )
    
    return updated_user