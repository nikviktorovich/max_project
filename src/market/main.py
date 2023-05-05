import logging

from fastapi import FastAPI
from fastapi import status
from fastapi import responses
from fastapi.middleware import cors

from . import database
from . import mappers
from . import repositories
from . import routers

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

database.Base.metadata.create_all(bind=database.engine)
mappers.start_mappers()

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


@app.exception_handler(Exception)
def global_exception_handler(request, exception):
    message = f"Failed to execute: {request.method}: {request.url}. Error: {exception}"
    logger.error(message)
    return responses.JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={'detail': 'Server error'}
    )


@app.exception_handler(ValueError)
def value_error_handler(request, exception):
    return responses.JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': str(exception)},
    )


@app.exception_handler(repositories.exceptions.NotFoundError)
def not_found_error_handler(request, exception):
    return responses.JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={'detail': str(exception)},
    )


# Routes
app.include_router(routers.auth.router)
app.include_router(routers.cart.router)
app.include_router(routers.image.router)
app.include_router(routers.product.router)
app.include_router(routers.product_image.router)
app.include_router(routers.user.router)
