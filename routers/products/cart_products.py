from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, insert, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.base import get_async_session
from models.cart_product import CartProduct
from models.user import User
from routers.auth.auth_bearer import JWTBearer
from schemas.cart_product import CartProductUpdate

router = APIRouter(
    prefix="/cart",
    tags=['cart']
)


@router.get("/add")
async def add_cart_product(product_id: int, quantity: int,
                           user: User = Depends(JWTBearer()),
                           session: AsyncSession = Depends(get_async_session)):
    statement = insert(CartProduct).values(product_id=product_id, user_id=user.id, quantity=quantity)
    await session.execute(statement)
    await session.commit()

    return {"status": "success"}


@router.delete("/remove")
async def remove_cart_product(cart_product_id: int,
                              user: User = Depends(JWTBearer()),
                              session: AsyncSession = Depends(get_async_session)):
    statement = delete(CartProduct).join(User, User.id == user.id).where(CartProduct.id == cart_product_id)
    await session.execute(statement)
    await session.commit()

    return {"status": "success"}


@router.put("/update")
async def update_cart_product(cart_product_id: int,
                              updated_product: CartProductUpdate,
                              user: User = Depends(JWTBearer()),
                              session: AsyncSession = Depends(get_async_session)):
    statement = update(CartProduct).where(CartProduct.id == cart_product_id).values(updated_product.dict())
    await session.execute(statement)
    await session.commit()

    return {"status": "success"}


@router.get("/all")
async def get_all_cart_product(user: User = Depends(JWTBearer()),
                               session: AsyncSession = Depends(get_async_session)):
    query = select(CartProduct).where(CartProduct.user_id == user.id)
    result = await session.execute(query)

    list = []
    for key, category in enumerate(result.fetchall()):
        list.append(jsonable_encoder(category[0]))

    return list
