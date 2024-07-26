from datetime import datetime

import phonenumbers
import requests
from fastapi import HTTPException

from config import RECAPTCHA_SECRET_KEY


def is_phone_number_valid(phone_number: str):
    try:
        mobile_phone_is_valid = phonenumbers.is_valid_number(phonenumbers.parse(phone_number))
    except:
        raise HTTPException(status_code=422, detail="Phone number is not valid!")

    if not mobile_phone_is_valid:
        raise HTTPException(status_code=422, detail="Phone number is not valid!")


def is_otp_expired(otp_expires: datetime):
    return otp_expires < datetime.utcnow()


def verify_captcha(host, captcha: str):
    url = "https://www.google.com/recaptcha/api/siteverify"
    params = {
        'secret': RECAPTCHA_SECRET_KEY,
        'response': captcha,
        'remoteip': host
    }

    verify_rs = requests.get(url, params=params, verify=True)
    verify_rs = verify_rs.json()
    status = verify_rs.get("success", False)

    if not status:
        raise HTTPException(status_code=400, detail="Captcha Validation Failed!")

    return status
