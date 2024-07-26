from typing import Optional

from pydantic import BaseModel


class ProductCreate(BaseModel):
    product_name: str
    image_path: str

    short_description: str
    product_description: str

    measure: str
    price: float
    quantity: int
    product_weight: int


class ProductUpdate(BaseModel):
    product_name: Optional[str]
    image_path: Optional[str]

    short_description: Optional[str]
    product_description: Optional[str]

    price: Optional[float]
    quantity: Optional[int]
    product_weight: Optional[int]
