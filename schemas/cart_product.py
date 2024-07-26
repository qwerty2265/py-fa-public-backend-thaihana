from typing import Optional

from pydantic import BaseModel


class CartProductCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int


class CartProductUpdate(BaseModel):
    quantity: Optional[int]

