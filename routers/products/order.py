from typing import List

from fastapi import APIRouter, Depends, Body
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select, insert, desc
from sqlalchemy.ext.asyncio import AsyncSession

from models.base import get_async_session
from models.order import Order, OrderProduct

import datetime

from models.product import Product
from models.user import User
from routers.auth.auth_bearer import JWTBearer
from utils import send_message

router = APIRouter(
    prefix="/orders",
    tags=['order']
)


class CartProduct(BaseModel):
    product_id: int
    quantity: int


@router.get("/active_orders")
async def get_active_orders(session: AsyncSession = Depends(get_async_session),
                            user: User = Depends(JWTBearer())):
    query = select(Order).where(Order.active).where(Order.mobile_phone == user.mobile_phone)
    result = await session.execute(query)

    list = []
    for key, product in enumerate(result.fetchall()):
        list.append(jsonable_encoder(product[0]))

    return list


@router.post("/create", response_model=None)
async def create_order(user: User = Depends(JWTBearer()),
                       cart_products: List[CartProduct] = Body(..., embed=True),
                       session: AsyncSession = Depends(get_async_session)):
    query_newest = select(Order).order_by(desc(Order.created_at)).limit(1)
    result_newest = (await session.execute(query_newest)).fetchall()

    final_id = 1
    dt_now = datetime.datetime.now()
    today = f"{dt_now.day:02}{dt_now.month:02}{dt_now.year}"
    if len(result_newest) != 0 and result_newest[0][0].order_number[0:8] == today:
        final_id = int(result_newest[0][0].order_number[-5:]) + 1

    new_order_number = f"{today}{final_id:05}"

    statement = insert(Order).values(mobile_phone=user.mobile_phone, order_number=new_order_number, created_at=datetime.datetime.utcnow())
    await session.execute(statement)
    await session.commit()

    order_query = select(Order).where(Order.order_number == new_order_number)
    order_result = (await session.execute(order_query)).first()[0]

    ids = []
    quantity_to_id = {}
    for product in cart_products:
        statement = insert(OrderProduct).values(order_id=order_result.id, product_id=product.product_id,
                                                quantity=product.quantity)
        await session.execute(statement)

        ids.append(product.product_id)
        quantity_to_id[product.product_id] = product.quantity

    await session.commit()

    product_query = select(Product).filter(Product.id.in_(ids))
    result = await session.execute(product_query)

    list = []
    for key, product in enumerate(result.fetchall()):
        list.append(jsonable_encoder(product[0]))

    product_msg = ""
    for key, product in enumerate(list):
        product_msg += f"       {key + 1}. {product['product_name']}, {product['price']}tg " \
                       f"в количестве: {quantity_to_id[product['id']]}\n"

    send_message(f"""
    Заказ №{new_order_number},
        Телефон: {user.mobile_phone},
        Товары: 
{product_msg}
    """)

    return jsonable_encoder(order_result)
