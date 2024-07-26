from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.base import get_async_session
from models.user import User
from routers.auth.auth_bearer import JWTBearer

router = APIRouter(
    prefix="/auth",
    tags=['auth']
)


@router.get("/user/me")
async def me(user: User = Depends(JWTBearer()), session: AsyncSession = Depends(get_async_session)):

    query = select(User).where(User.mobile_phone == user.mobile_phone)
    existing_user = (await session.execute(query)).first()

    user_dict = jsonable_encoder(existing_user[0])
    user_dict.pop("hashed_password")
    user_dict.pop("otp")
    user_dict.pop("otp_expires")

    return user_dict
