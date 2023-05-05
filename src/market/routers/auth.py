from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import security
from fastapi import status
from sqlalchemy.orm import Session
from .. import deps
from .. import repositories
from .. import schemas
from .. import services

router = APIRouter(
    tags=['auth']
)


@router.post('/token', response_model=schemas.Token)
async def login(
    form_data: security.OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(deps.get_db),
):
    """Authorizes user and returns an access token."""
    repo = repositories.UserRepository(db)
    auth_service = services.AuthService(repo)
    token = auth_service.login(form_data.username, form_data.password)

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    
    return token


@router.post('/signup', response_model=schemas.Token)
async def signup(
    user_schema: schemas.UserCreate = Depends(deps.get_user_create_form_data),
    db: Session = Depends(deps.get_db),
):
    """Allows user to sign up and returns an access token."""
    repo = repositories.UserRepository(db)
    auth_service = services.AuthService(repo)

    auth_service.register_user(
        username=user_schema.username,
        password=user_schema.password,
        full_name=user_schema.full_name,
    )
    db.commit()

    token = auth_service.login(user_schema.username, user_schema.password)

    return token
