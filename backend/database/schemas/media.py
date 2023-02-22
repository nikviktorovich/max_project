import pydantic


class ImageBase(pydantic.BaseModel):
    media_path: str


class ImageCreate(ImageBase):
    pass


class Image(ImageBase):
    id: int
    
    class Config:
        orm_mode = True
