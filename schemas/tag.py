from typing import Optional

from pydantic import BaseModel


class TagCreate(BaseModel):
    tag_name: str
    image_path: str


class TagUpdate(BaseModel):
    tag_name: Optional[str]
    image_path: Optional[str]
