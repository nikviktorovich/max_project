import contextlib
import logging

from fastapi import FastAPI
from fastapi import status
from fastapi import responses
from fastapi.middleware import cors

import market.apps.fastapi_app.routers
import market.common.errors
import market.config
import market.database.orm
import market.database.mappers

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

market.database.mappers.start_mappers()


@contextlib.asynccontextmanager
async def app_lifespan(app: FastAPI):
    # market.database.orm.Base.metadata.create_all(
    #     bind=market.config.get_database_engine(),
    # )
    yield

app = FastAPI(lifespan=app_lifespan)

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


@app.exception_handler(market.common.errors.NotFoundError)
def not_found_error_handler(request, exception):
    return responses.JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={'detail': str(exception)},
    )


# Routes
app.include_router(market.apps.fastapi_app.routers.auth.router)
app.include_router(market.apps.fastapi_app.routers.cart.router)
app.include_router(market.apps.fastapi_app.routers.image.router)
app.include_router(market.apps.fastapi_app.routers.product.router)
app.include_router(market.apps.fastapi_app.routers.product_image.router)
app.include_router(market.apps.fastapi_app.routers.user.router)
