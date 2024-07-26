from pydantic import BaseModel
from typing import Optional


class HeadingCreate(BaseModel):
    visible: bool

    heading_name: str
    image_path: str

    heading_description: str


class HeadingUpdate(BaseModel):
    visible: Optional[bool]

    heading_name: Optional[str]
    image_path: Optional[str]

    heading_description: Optional[str]
