from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.base import get_async_session
from models.user import User
from routers.auth.auth_handler import signJWT
from schemas.user import UserLoginSchema

import bcrypt

router = APIRouter(
    prefix="/auth",
    tags=['auth']
)


@router.post("/user/login")
async def login(user: UserLoginSchema = Body(...), session: AsyncSession = Depends(get_async_session)):

    query = select(User).where(User.mobile_phone == user.mobile_phone)
    existing_user = (await session.execute(query)).first()

    if existing_user is None:
        raise HTTPException(status_code=400, detail="Incorrect login or password!")

    byte_password = user.password.encode('utf-8')

    if not bcrypt.checkpw(byte_password, existing_user[0].hashed_password.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Incorrect login or password!")

    return signJWT(user.mobile_phone)
