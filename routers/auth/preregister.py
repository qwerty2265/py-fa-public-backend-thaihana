import random
from datetime import datetime, timedelta

from fastapi import APIRouter, Body, HTTPException, Depends, Request
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.base import get_async_session
from models.user import User
from schemas.user import UserPreRegisterSchema, UserOtpCheckSchema
from utils import send_otp
from .auth_utils import is_phone_number_valid, is_otp_expired, verify_captcha

router = APIRouter(
    prefix="/auth",
    tags=['auth']
)


@router.post("/user/preregister")
async def preregister(request: Request, user: UserPreRegisterSchema = Body(...),
                      session: AsyncSession = Depends(get_async_session)):
    is_phone_number_valid(user.mobile_phone)

    query = select(User).where(User.mobile_phone == user.mobile_phone)
    existing_user = (await session.execute(query)).first()

    if existing_user is not None and existing_user[0].is_verified:
        raise HTTPException(status_code=400, detail="User already exists!")

    status = verify_captcha(request.client.host, user.captcha)

    if not status:
        raise HTTPException(status_code=400, detail="Captcha Validation Failed!")

    user_dict = user.dict()

    user_dict.pop("captcha")

    user_dict["hashed_password"] = "null"
    user_dict["first_name"] = "null"
    user_dict["last_name"] = "null"

    otp = random.randint(100000, 999999)
    user_dict["otp"] = otp
    user_dict["otp_expires"] = datetime.utcnow() + timedelta(minutes=10)

    send_otp(user.mobile_phone.replace("+", ""), otp)

    statement = insert(User).values(**user_dict)

    if existing_user is not None:
        statement = update(User).where(User.mobile_phone == user.mobile_phone).values(**user_dict)

    await session.execute(statement)
    await session.commit()

    return {"status": "success"}


@router.post("/user/otp_check")
async def otp_check(user: UserOtpCheckSchema = Body(...), session: AsyncSession = Depends(get_async_session)):
    is_phone_number_valid(user.mobile_phone)

    query = select(User).where(User.mobile_phone == user.mobile_phone).where(User.otp == user.otp)
    existing_user = (await session.execute(query)).first()

    return existing_user is not None and not is_otp_expired(existing_user[0].otp_expires) \
        and user.otp == existing_user[0].otp
