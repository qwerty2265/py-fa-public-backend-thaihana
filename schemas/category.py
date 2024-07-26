from pydantic import BaseModel
from typing import Optional


class CategoryCreate(BaseModel):
    parent_id: int
    heading_id: int

    category_name: str
    image_path: str

    category_description: str


class CategoryUpdate(BaseModel):
    parent_id: Optional[int]
    heading_id: Optional[int]

    category_name: Optional[str]
    image_path: Optional[str]

    category_description: Optional[str]
