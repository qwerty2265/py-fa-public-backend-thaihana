import bcrypt
import random
from datetime import datetime, timedelta

from fastapi import APIRouter, Body, HTTPException, Depends, Request
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.base import get_async_session
from models.user import User
from schemas.user import UserPreRegisterSchema, UserResetPasswordSchema
from utils import send_otp
from .auth_utils import is_phone_number_valid, is_otp_expired, verify_captcha

router = APIRouter(
    prefix="/auth",
    tags=['auth']
)


@router.post("/user/forgot_password")
async def forgot_password(request: Request, user: UserPreRegisterSchema = Body(...), session: AsyncSession = Depends(get_async_session)):

    is_phone_number_valid(user.mobile_phone)

    query = select(User).where(User.mobile_phone == user.mobile_phone)
    existing_user = (await session.execute(query)).first()

    if existing_user is None or not existing_user[0].is_verified:
        raise HTTPException(status_code=400, detail="User doesn't exist!")

    status = verify_captcha(request.client.host, user.captcha)

    if not status:
        raise HTTPException(status_code=400, detail="Captcha Validation Failed!")

    user_dict = user.dict()

    user_dict.pop("captcha")

    otp = random.randint(100000, 999999)
    user_dict["otp"] = otp
    user_dict["otp_expires"] = datetime.utcnow() + timedelta(minutes=10)

    send_otp(user.mobile_phone.replace("+", ""), otp)

    statement = update(User).where(User.mobile_phone == user.mobile_phone).values(**user_dict)

    await session.execute(statement)
    await session.commit()

    return {"status": "success"}


@router.post("/user/reset_password")
async def reset_password(user: UserResetPasswordSchema = Body(...), session: AsyncSession = Depends(get_async_session)):

    is_phone_number_valid(user.mobile_phone)

    query = select(User).where(User.mobile_phone == user.mobile_phone)
    existing_user = (await session.execute(query)).first()

    if existing_user is None or not existing_user[0].is_verified:
        raise HTTPException(status_code=400, detail="User doesn't exist!")

    if is_otp_expired(existing_user[0].otp_expires):
        raise HTTPException(status_code=400, detail="OTP is expired!")

    if existing_user[0].otp != user.otp:
        raise HTTPException(status_code=400, detail="OTP is wrong!")

    salt = bcrypt.gensalt()
    byte_password = user.new_password.encode('utf-8')
    new_hashed_password = bcrypt.hashpw(byte_password, salt).decode('utf-8')

    statement = update(User).where(User.mobile_phone == user.mobile_phone).values(hashed_password=new_hashed_password)

    await session.execute(statement)
    await session.commit()

    return {"status": "success"}


