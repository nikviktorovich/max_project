import fastapi
import fastapi.middleware.cors


app = fastapi.FastAPI()

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
