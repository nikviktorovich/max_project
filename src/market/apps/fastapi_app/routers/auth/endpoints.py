import uuid

import pydantic
from fastapi import APIRouter
from fastapi import Body
from fastapi import Depends
from fastapi import HTTPException
from fastapi import security
from fastapi import status

import market.services.auth
from market.apps.fastapi_app import deps
from market.apps.fastapi_app.routers.auth import schemas
from market.services import unit_of_work

router = APIRouter(
    tags=['auth'],
)


@router.post('/token', response_model=schemas.Token)
async def login(
    form_data: security.OAuth2PasswordRequestForm = Depends(),
    uow: unit_of_work.UnitOfWork = Depends(deps.get_uow),
):
    """Authorizes user and returns an access token."""
    auth_service = market.services.auth.AuthServiceImpl(uow.users)
    token = auth_service.login(form_data.username, form_data.password)

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    
    return schemas.Token.from_orm(token)


def get_user_create_form_data(
    form_data: security.OAuth2PasswordRequestForm = Depends(),
    full_name: str = Body(default=''),
) -> schemas.UserCreate:
    try:
        return schemas.UserCreate(
            username=form_data.username,
            password=form_data.password,
            full_name=full_name,
        )
    except pydantic.ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.errors()
        )


@router.post('/signup', response_model=schemas.Token)
async def signup(
    user_schema: schemas.UserCreate = Depends(get_user_create_form_data),
    uow: unit_of_work.UnitOfWork = Depends(deps.get_uow),
):
    """Allows user to sign up and returns an access token."""
    auth_service = market.services.auth.AuthServiceImpl(uow.users)

    auth_service.register_user(
        user_id=uuid.uuid4(),
        username=user_schema.username,
        password=user_schema.password,
        full_name=user_schema.full_name,
    )
    uow.commit()

    token = auth_service.login(user_schema.username, user_schema.password)

    return schemas.Token.from_orm(token)
