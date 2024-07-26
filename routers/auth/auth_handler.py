import time
from typing import Dict

import jwt
from fastapi import HTTPException

import config

JWT_SECRET = config.SECRET
JWT_ALGORITHM = "HS256"


def token_response(token: str):
    return {
        "access_token": token
    }


def signJWT(mobile_phone: str) -> Dict[str, str]:
    payload = {
        "mobile_phone": mobile_phone,
        "expires": time.time() + 30 * 24 * 60 * 60
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(token)


def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        if decoded_token["expires"] < time.time():
            raise HTTPException(status_code=401, detail="Token is expired!")

        return decoded_token

    except:
        raise HTTPException(status_code=422, detail="Unprocessable entity")
