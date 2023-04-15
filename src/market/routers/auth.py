from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import security
from fastapi import status
from sqlalchemy.orm import Session
from .. import auth
from .. import deps
from .. import schemas

router = APIRouter(
    tags=['auth']
)


@router.post('/token', response_model=schemas.Token)
async def login(
    form_data: security.OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(deps.get_db),
):
    """Authorizes user and returns an access token."""
    login_result = auth.login(db, form_data.username, form_data.password)
    if login_result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    return login_result


@router.post('/signup', response_model=schemas.Token)
async def signup(token: schemas.Token = Depends(deps.register_user)):
    """Allows user to sign up and returns an access token."""
    return token
