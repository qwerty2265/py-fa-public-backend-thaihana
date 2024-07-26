import bcrypt
from fastapi import APIRouter, Body, HTTPException, Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.base import get_async_session
from models.user import User
from routers.auth.auth_handler import signJWT
from schemas.user import UserRegisterSchema
from .auth_utils import is_phone_number_valid, is_otp_expired

router = APIRouter(
    prefix="/auth",
    tags=['auth']
)


@router.post("/user/register")
async def register(user: UserRegisterSchema = Body(...), session: AsyncSession = Depends(get_async_session)):

    is_phone_number_valid(user.mobile_phone)

    query = select(User).where(User.mobile_phone == user.mobile_phone)
    existing_user = (await session.execute(query)).first()

    if existing_user is None:
        raise HTTPException(status_code=400, detail="PreRegistration should be done first!")

    if existing_user[0].is_verified:
        raise HTTPException(status_code=400, detail="User already exists!")

    if is_otp_expired(existing_user[0].otp_expires):
        raise HTTPException(status_code=400, detail="OTP is expired!")

    if existing_user[0].otp != user.otp:
        raise HTTPException(status_code=400, detail="OTP is wrong!")

    user_dict = user.dict()

    user_dict.pop("mobile_phone")
    user_dict["is_verified"] = True

    salt = bcrypt.gensalt()
    password = user_dict.pop("password")
    byte_password = password.encode('utf-8')
    user_dict["hashed_password"] = bcrypt.hashpw(byte_password, salt).decode('utf-8')

    statement = update(User).values(**user_dict)
    await session.execute(statement)
    await session.commit()

    return signJWT(user.mobile_phone)
