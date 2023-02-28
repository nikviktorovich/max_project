import fastapi.exceptions
import pydantic
import auth
import database
from typing import List, Optional
from fastapi import Body
from fastapi import Depends
from fastapi import FastAPI
from fastapi import Form
from fastapi import HTTPException
from fastapi import security
from fastapi import status
from fastapi.middleware import cors
from sqlalchemy.orm import Session
from database import crud
from database import schemas

database.Base.metadata.create_all(bind=database.engine)


oauth2_scheme = security.OAuth2PasswordBearer(tokenUrl='token')

app = FastAPI()

# CORS configuration
origins = [
    'http://localhost:*',
]

app.add_middleware(
    middleware_class=cors.CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Routes
@app.get('/')
async def get_index(token: str = Depends(oauth2_scheme)):
    return {'token': token}


@app.post('/token')
async def login(
    form_data: security.OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Returns:
        access_token
        token_type
    """
    login_result = auth.login(db, form_data.username, form_data.password)
    if login_result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    return login_result


def get_user_create_form_data(
    username: str = Body(),
    password: str = Body(),
    full_name: str = Body(default=''),
) -> schemas.UserCreate:
    try:
        return schemas.UserCreate(
            username=username,
            full_name=full_name,
            password=password
        )
    except pydantic.ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.errors()
        )


def register_user(
    user_data: schemas.UserCreate = Depends(get_user_create_form_data),
    form_data: security.OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    try:
        token = auth.register_user(db, user_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    else:
        return token


@app.post('/signup')
async def signup(token: schemas.Token = Depends(register_user)):
    """
    """
    
    return token


@app.get('/products', response_model=List[schemas.ProductRead])
def get_products(
    offset: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud.get_products(db, offset, limit)
