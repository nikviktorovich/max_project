import uuid

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import security
from fastapi import status

import market.services
from market.apps.fastapi_app import deps
from market.modules.user import schemas
from market.services import unit_of_work

router = APIRouter(
    tags=['auth']
)


@router.post('/token', response_model=schemas.Token)
async def login(
    form_data: security.OAuth2PasswordRequestForm = Depends(),
    uow: unit_of_work.UnitOfWork = Depends(deps.get_uow),
):
    """Authorizes user and returns an access token."""
    auth_service = market.services.AuthService(uow.users)
    token = auth_service.login(form_data.username, form_data.password)

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    
    return schemas.Token.from_orm(token)


@router.post('/signup', response_model=schemas.Token)
async def signup(
    user_schema: schemas.UserCreate = Depends(deps.get_user_create_form_data),
    uow: unit_of_work.UnitOfWork = Depends(deps.get_uow),
):
    """Allows user to sign up and returns an access token."""
    auth_service = market.services.AuthService(uow.users)

    auth_service.register_user(
        user_id=uuid.uuid4(),
        username=user_schema.username,
        password=user_schema.password,
        full_name=user_schema.full_name,
    )
    uow.commit()

    token = auth_service.login(user_schema.username, user_schema.password)

    return schemas.Token.from_orm(token)
