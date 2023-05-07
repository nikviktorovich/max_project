import os
from typing import Optional
from urllib.parse import urljoin

import pydantic


class ImageBase(pydantic.BaseModel):
    image: str


class ImageCreate(ImageBase):
    pass


class ImageRead(ImageBase):
    id: int

    @pydantic.validator('image')
    def adjust_media_path(cls, v):
        """Making URL to reach the image"""
        media_url_root = os.getenv('MEDIA_URL_ROOT')
        if media_url_root is None:
            raise RuntimeError('MEDIA_URL_ROOT is not specified')
        return urljoin(media_url_root, v)

    class Config:
        orm_mode = True


class Image(ImageBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True
