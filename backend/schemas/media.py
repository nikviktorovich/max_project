import pydantic


class Image(pydantic.BaseModel):
    id: int
    media_path: str
