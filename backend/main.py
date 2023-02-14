import fastapi
import fastapi.middleware.cors
import database
import models

models.Base.metadata.create_all(bind=database.engine)

app = fastapi.FastAPI()

# CORS configuration
origins = [
    'http://localhost:*',
]

app.add_middleware(
    middleware_class=fastapi.middleware.cors.CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


# Routes
...